from datetime import datetime
from logging import getLogger

from django.template.loader import render_to_string

from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (RetrieveUpdateDestroyAPIView,
                                     ListCreateAPIView)

from neomodel import CypherException

from sagebrew import errors

from sb_docstore.utils import (get_dynamo_table)
from sb_votes.utils import determine_vote_type
from plebs.neo_models import Pleb

from .serializers import PostSerializerNeo
from .neo_models import SBPost


logger = getLogger('loggly_logs')


class WallPostsRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializerNeo
    permission_classes = (IsAuthenticated,)
    lookup_field = "username"
    lookup_url_kwarg = "post_uuid"

    def get_queryset(self):
        try:
            queryset = SBPost.nodes.all()
        except(CypherException, IOError):
            logger.exception("CommentGenericViewSet queryset")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return sorted(queryset, key=lambda k: k.created)

    def get_object(self):
        try:
            queryset = SBPost.nodes.get(
                object_uuid=self.kwargs[self.lookup_url_kwarg])
        except(CypherException, IOError):
            logger.exception("CommentRetrieveUpdateDestroy get_object")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return queryset


class WallPostsListCreate(ListCreateAPIView):
    serializer_class = PostSerializerNeo
    permission_classes = (IsAuthenticated,)
    lookup_field = "username"

    def get_queryset(self):
        try:
            wall = Pleb.nodes.get(username=self.kwargs[self.lookup_field])
            queryset = wall.posts.all()
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

        serializer = PostSerializerNeo(data=comment_data,
                                       context={"request": request})
        if serializer.is_valid():
            # TODO should probably spawn neo connection off into task
            # and instead make relation in dynamo. Can include the given
            # uuid in the task spawned off. Also as mentioned in the
            # serializer, we should capture the user from the request,
            # get the pleb (maybe in the task) and use that to call
            # comment_relations
            owner = Pleb.nodes.get(username=request.user.username)
            wall_owner = Pleb.nodes.get(username=self.kwargs[self.lookup_field])
            instance = serializer.save(owner=owner, wall_owner=wall_owner)

            serializer = PostSerializerNeo(instance,
                                           context={"request": request})
            put_item = dict(serializer.data)
            put_item['parent_object'] = wall_owner.username
            table = get_dynamo_table("posts")
            table.put_item(data=put_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def post_renderer(request, username=None):
    '''
    This is a intermediate step on the way to utilizing a JS Framework to
    handle template rendering.
    '''
    html_array = []
    id_array = []
    args = []
    kwargs = {"username": username}
    posts = WallPostsListCreate.as_view()(request, *args, **kwargs)
    for post in posts.data['results']:
        post['vote_type'] = determine_vote_type(
            post['object_uuid'], request.user.username)
        post['last_edited_on'] = datetime.strptime(
            post['last_edited_on'][:len(post['last_edited_on']) - 6],
            '%Y-%m-%dT%H:%M:%S.%f')
        html_array.append(render_to_string('question_summary.html',  post))
        id_array.append(post["object_uuid"])
    posts.data['results'] = {"html": html_array, "ids": id_array}
    return Response(posts.data, status=status.HTTP_200_OK)