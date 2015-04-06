from datetime import datetime
from logging import getLogger

from django.template.loader import render_to_string

from rest_framework.decorators import (api_view, permission_classes)
from rest_framework import viewsets
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


class PostsViewSet(viewsets.GenericViewSet):
    serializer_class = PostSerializerNeo
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"
    lookup_url_kwarg = "object_uuid"

    def get_queryset(self):
        try:
            queryset = SBPost.nodes.all()
        except(CypherException, IOError):
            logger.exception("CommentGenericViewSet queryset")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return sorted(queryset, key=lambda k: k.created, reverse=True)

    def get_object(self):
        try:
            queryset = SBPost.nodes.get(
                object_uuid=self.kwargs[self.lookup_url_kwarg])
        except(CypherException, IOError):
            logger.exception("CommentRetrieveUpdateDestroy get_object")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return queryset

    def list(self, request):
        response = {"status": status.HTTP_501_NOT_IMPLEMENTED,
                    "detail": "We do not allow users to query all the posts on"
                              "the site.",
                    "developer_message":
                        "We're working on enabling easier access to posts based"
                        "on user's friends and walls they have access to. "
                        "However this endpoint currently does not return any "
                        "post data. Please utilize the 'wall' endpoint for "
                        "the time being. It is located at "
                        "'/v1/profiles/<username>/wall/'. It will provide "
                        "you with all the posts for a given wall. You still "
                        "must be friends with the user to access the "
                        "information"}
        return Response(response, status=status.HTTP_501_NOT_IMPLEMENTED)

    def create(self, request):
        response = {"status": status.HTTP_501_NOT_IMPLEMENTED,
                    "detail": "We do not allow users to create that are not "
                              "associated with a wall.",
                    "developer_message":
                        "We're working on enabling additional ways to allow "
                        "for users to save posts but for the time being"
                        "we require that users utilize the "
                        "'/v1/profiles/<username>/wall/' endpoint to create"
                        "new posts."}
        return Response(response, status=status.HTTP_501_NOT_IMPLEMENTED)

    def retrieve(self, request, object_uuid=None):
        response = {"status": status.HTTP_501_NOT_IMPLEMENTED,
                    "detail": "We do not allow users to retrieve specific "
                              "posts through this endpoint at this time.",
                    "developer_message": "We do not allow users to retrieve "
                                         "specific posts from this endpoint "
                                         "currently. To do so please utilize "
                                         "the '/v1/profiles/<username>/"
                                         "wall/<post_uuid>/' endpoint."}
        return Response(response, status=status.HTTP_200_OK)

    def update(self, request, object_uuid=None):
        pass

    def partial_update(self, request, object_uuid=None):
        pass

    def destroy(self, request, object_uuid=None):
        pass


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

        return sorted(queryset, key=lambda k: k.created, reverse=True)

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
        queryset = sorted(queryset, key=lambda k: k.created, reverse=True)

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
        post_data = request.data
        post_data['parent_object'] = self.kwargs[self.lookup_field]

        serializer = PostSerializerNeo(data=post_data,
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
            html = request.query_params.get('html', 'false').lower()
            if html == "true":
                html_array = []
                id_array = []
                post = dict(serializer.data)
                post['vote_type'] = determine_vote_type(
                    post['object_uuid'], request.user.username)
                post['last_edited_on'] = datetime.strptime(
                    post['last_edited_on'][:len(post['last_edited_on']) - 6],
                    '%Y-%m-%dT%H:%M:%S.%f')
                post["current_user"] = request.user.username
                html_array.append(render_to_string('post.html',  post))
                id_array.append(post["object_uuid"])
                return Response({"html": html_array, "ids": id_array},
                                status=status.HTTP_200_OK)
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
        post["current_user"] = request.user.username
        html_array.append(render_to_string('post.html',  post))
        id_array.append(post["object_uuid"])
    posts.data['results'] = {"html": html_array, "ids": id_array}
    return Response(posts.data, status=status.HTTP_200_OK)