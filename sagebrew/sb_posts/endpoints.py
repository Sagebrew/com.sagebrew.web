from uuid import uuid1
from datetime import datetime
from logging import getLogger

from django.template.loader import render_to_string
from django.template import RequestContext

from rest_framework.decorators import (api_view, permission_classes)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (ListCreateAPIView)

from neomodel import db

from api.permissions import IsOwnerOrAdmin
from api.utils import spawn_task
from sb_base.views import ObjectRetrieveUpdateDestroy
from sb_notifications.tasks import spawn_notifications

from .serializers import PostSerializerNeo
from .neo_models import Post


logger = getLogger('loggly_logs')


class PostsViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializerNeo
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)
    queryset = Post.nodes.all()
    lookup_field = "object_uuid"

    def get_object(self):
        return Post.nodes.get(object_uuid=self.kwargs[self.lookup_field])

    def perform_destroy(self, instance):
        instance.content = ""
        instance.to_be_deleted = True
        instance.save()
        return instance

    def list(self, request, *args, **kwargs):
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

    def create(self, request, *args, **kwargs):
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


class WallPostsRetrieveUpdateDestroy(ObjectRetrieveUpdateDestroy):
    serializer_class = PostSerializerNeo
    lookup_field = "object_uuid"
    lookup_url_kwarg = "post_uuid"

    def get_object(self):
        return Post.nodes.get(
            object_uuid=self.kwargs[self.lookup_url_kwarg])


class WallPostsListCreate(ListCreateAPIView):
    serializer_class = PostSerializerNeo
    permission_classes = (IsAuthenticated,)
    lookup_field = "username"

    def get_queryset(self):
        """
        Used query because match isn't working and filter doesn't work on
        all().
        """
        query = "MATCH (a:Pleb {username:'%s'})-[:OWNS_WALL]->" \
                "(b:Wall)-[:HAS_POST]->(c) WHERE c.to_be_deleted=false" \
                " RETURN c ORDER BY c.created " \
                "DESC" % (self.kwargs[self.lookup_field])
        res, col = db.cypher_query(query)
        return [Post.inflate(row[0]) for row in res]

    def create(self, request, *args, **kwargs):
        post_data = request.data
        post_data['parent_object'] = self.kwargs[self.lookup_field]

        serializer = self.get_serializer(data=post_data,
                                         context={"request": request})
        if serializer.is_valid():
            serializer.save(wall_owner=self.kwargs[self.lookup_field])
            serializer = serializer.data
            data = {
                "from_pleb": request.user.username,
                "sb_object": serializer['object_uuid'],
                "url": serializer['url'],
                "to_plebs": [self.kwargs[self.lookup_field], ],
                "notification_id": str(uuid1())
            }
            spawn_task(task_func=spawn_notifications, task_param=data)
            html = request.query_params.get('html', 'false').lower()
            if html == "true":
                serializer["vote_count"] = str(serializer["vote_count"])
                serializer['last_edited_on'] = datetime.strptime(
                    serializer['last_edited_on'][:len(
                        serializer['last_edited_on']) - 6],
                    '%Y-%m-%dT%H:%M:%S.%f')
                context = RequestContext(request, serializer)
                return Response(
                    {
                        "html": [render_to_string('post.html', context)],
                        "ids": [serializer["object_uuid"]]
                    },
                    status=status.HTTP_200_OK)
            return Response(serializer, status=status.HTTP_200_OK)
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
        # This is a work around for django templates and our current
        # implementation of spacing for vote count in the template.
        post["vote_count"] = str(post["vote_count"])
        post['last_edited_on'] = datetime.strptime(
            post['last_edited_on'][:len(post['last_edited_on']) - 6],
            '%Y-%m-%dT%H:%M:%S.%f')
        context = RequestContext(request, post)
        html_array.append(render_to_string('post.html', context))
        id_array.append(post["object_uuid"])
    posts.data['results'] = {"html": html_array, "ids": id_array}
    return Response(posts.data, status=status.HTTP_200_OK)
