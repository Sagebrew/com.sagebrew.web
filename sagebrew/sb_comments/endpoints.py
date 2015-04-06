from datetime import datetime
from logging import getLogger

from django.template.loader import render_to_string

from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (RetrieveUpdateDestroyAPIView,
                                     ListCreateAPIView)

from neomodel.exception import CypherException

from sagebrew import errors
from sb_base.neo_models import SBContent
from sb_docstore.utils import (get_dynamo_table)
from sb_votes.utils import determine_vote_type
from plebs.neo_models import Pleb

from .neo_models import SBComment
from .serializers import CommentSerializer

logger = getLogger('loggly_logs')


class ObjectCommentsRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"
    lookup_url_kwarg = "comment_uuid"

    def get_queryset(self):
        try:
            queryset = SBComment.nodes.all()
        except(CypherException, IOError):
            logger.exception("CommentGenericViewSet queryset")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return sorted(queryset, key=lambda k: k.created)

    def get_object(self):
        try:
            queryset = SBComment.nodes.get(
                object_uuid=self.kwargs[self.lookup_url_kwarg])
        except(CypherException, IOError):
            logger.exception("CommentRetrieveUpdateDestroy get_object")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return queryset


class ObjectCommentsListCreate(ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        """
        # TODO need to reintegrate this. Removed it for the time being as we
        # transition over to a more consistent approach using serializers.
        # Hope is that we can do the query in Dynamo and just provide the
        # returned dicts almost as is and it appear the same as if the info
        # was coming from neo
        try:
            table = get_dynamo_table("comments")
            if isinstance(table, Exception) is True:
                logger.exception("QuestionGenericViewSet comment")
                raise table
            queryset = table.query_2(
                parent_object__eq=self.kwargs[self.lookup_field],
                created__gte="0"
            )
            converted = convert_dynamo_comments(queryset)
            for comment in converted:
                vote_type = get_vote(comment['object_uuid'],
                                     self.request.user.username)
                if vote_type is not None:
                    if vote_type['status'] == 2:
                        vote_type = None
                    else:
                        vote_type = str(bool(vote_type['status'])).lower()
                comment['vote_type'] = vote_type
            if converted:
                return converted
        except(JSONResponseError, IOError) as e:
            pass
        """
        try:
            queryset = SBContent.nodes.get(
                object_uuid=self.kwargs[self.lookup_field])
            queryset = queryset.comments.all()
        except(CypherException, IOError) as e:
            logger.exception("CommentGenericViewSet queryset")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        queryset = sorted(queryset, key=lambda k: k.created)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # As a note this if is the only difference between this list
        # implementation and the default ListModelMixin. Not sure if we need
        # to redefine everything...
        if isinstance(queryset, Response):
            return queryset
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True,
                                             context={"request": request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(
            queryset, context={"request": request}, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        comment_data = request.data
        comment_data['parent_object'] = self.kwargs[self.lookup_field]

        serializer = CommentSerializer(data=comment_data,
                                       context={"request": request})
        if serializer.is_valid():
            # TODO should probably spawn neo connection off into task
            # and instead make relation in dynamo. Can include the given
            # uuid in the task spawned off. Also as mentioned in the
            # serializer, we should capture the user from the request,
            # get the pleb (maybe in the task) and use that to call
            # comment_relations
            instance = serializer.save(
                owner=Pleb.nodes.get(username=request.user.username))
            parent_object = SBContent.nodes.get(
                object_uuid=self.kwargs[self.lookup_field])
            parent_object.comments.connect(instance)
            parent_object.save()
            serializer = CommentSerializer(instance,
                                           context={"request": request})
            put_item = dict(serializer.data)
            put_item['parent_object'] = parent_object.object_uuid
            table = get_dynamo_table("comments")
            table.put_item(data=put_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def comment_renderer(request, object_uuid=None):
    '''
    This is a intermediate step on the way to utilizing a JS Framework to
    handle template rendering.
    '''
    html_array = []
    id_array = []
    args = []
    kwargs = {"object_uuid": object_uuid}
    comments = ObjectCommentsListCreate.as_view()(request, *args, **kwargs)
    for comment in comments.data['results']:
        comment['vote_type'] = determine_vote_type(
            comment['object_uuid'], request.user.username)
        comment['last_edited_on'] = datetime.strptime(
            comment[
                'last_edited_on'][:len(comment['last_edited_on']) - 6],
            '%Y-%m-%dT%H:%M:%S.%f')
        comment["current_user_username"] = request.user.username
        html_array.append(render_to_string('sb_comments.html',  comment))
        id_array.append(comment["object_uuid"])
    comments.data['results'] = {"html": html_array, "ids": id_array}
    return Response(comments.data, status=status.HTTP_200_OK)