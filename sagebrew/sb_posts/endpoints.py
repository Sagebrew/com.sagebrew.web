from uuid import uuid1
from dateutil import parser

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
from plebs.neo_models import Pleb

from .serializers import PostSerializerNeo, PostEndpointSerializerNeo
from .neo_models import Post

from logging import getLogger
logger = getLogger('loggly_logs')


class PostsViewSet(viewsets.ModelViewSet):
    serializer_class = PostEndpointSerializerNeo
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    lookup_field = "object_uuid"

    def get_object(self):
        return Post.nodes.get(object_uuid=self.kwargs[self.lookup_field])

    def perform_destroy(self, instance):
        instance.content = ""
        instance.to_be_deleted = True
        instance.save()
        return instance

    def get_queryset(self):
        username = self.request.query_params.get('wall', None)
        if self.request.user.username == username or username is None:
            # Returns the posts for the current user's wall
            query = "MATCH (current:Pleb {username: '%s'})-[:OWNS_WALL]" \
                    "->(wall:Wall)-[:HAS_POST]->(c) WHERE " \
                    "c.to_be_deleted=false RETURN c " \
                    "ORDER BY c.created DESC" % self.request.user.username
        else:
            # Returns the posts only if the current user is friends with the
            # owner of the current wall
            query = "MATCH (current:Pleb {username: '%s'})-" \
                    "[friend:FRIENDS_WITH]->(wall_pleb:Pleb {username: " \
                    "'%s'})-" \
                    "[:OWNS_WALL]->(wall:Wall)-[:HAS_POST]->(c) " \
                    "WHERE c.to_be_deleted=false RETURN " \
                    "CASE friend.currently_friends WHEN True THEN c " \
                    "END AS result ORDER BY result.created DESC" % (
                        self.request.user.username, username)
        res, _ = db.cypher_query(query)
        return res

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        page = [Post.inflate(row[0]) for row in page]
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            wall_pleb = Pleb.get(
                serializer.validated_data.get('wall', request.user.username))
            friend_with = wall_pleb.is_friends_with(request.user.username)
            if friend_with is False and wall_pleb.username != \
                    request.user.username:
                return Response({"detail": "Sorry you are not friends with this"
                                           " person.",
                                 "status": status.HTTP_400_BAD_REQUEST},
                                status=status.HTTP_400_BAD_REQUEST)
            instance = serializer.save(wall_owner_profile=wall_pleb)
            serializer = serializer.data
            spawn_task(task_func=spawn_notifications, task_param={
                "from_pleb": request.user.username,
                "sb_object": serializer['object_uuid'],
                "url": serializer['url'],
                "to_plebs": [wall_pleb.username, ],
                "notification_id": str(uuid1()),
                "action_name": instance.action_name
            })
            return Response(serializer, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        if self.request.user.username == self.kwargs[self.lookup_field]:
            # Returns the posts for the current user's wall
            query = "MATCH (current:Pleb {username: '%s'})-[:OWNS_WALL]" \
                    "->(wall:Wall)-[:HAS_POST]->(c) WHERE " \
                    "c.to_be_deleted=false RETURN c " \
                    "ORDER BY c.created DESC" % self.request.user.username
        else:
            # Returns the posts only if the current user is friends with the
            # owner of the current wall
            query = "MATCH (current:Pleb {username: '%s'})-" \
                    "[friend:FRIENDS_WITH]->(wall_pleb:Pleb {username: " \
                    "'%s'})-" \
                    "[:OWNS_WALL]->(wall:Wall)-[:HAS_POST]->(c) " \
                    "WHERE c.to_be_deleted=false RETURN " \
                    "CASE friend.currently_friends WHEN True THEN c " \
                    "END AS result ORDER BY result.created DESC" % (
                        self.request.user.username,
                        self.kwargs[self.lookup_field])
        res, _ = db.cypher_query(query)
        return res

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        page = [Post.inflate(row[0]) for row in page]
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        wall_pleb = Pleb.get(self.kwargs[self.lookup_field])
        friend_with = wall_pleb.is_friends_with(request.user.username)
        if friend_with is False and wall_pleb.username != request.user.username:
            return Response({"detail": "Sorry you are not friends with this"
                                       " person."},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(wall_owner_profile=wall_pleb)
            serializer = serializer.data
            spawn_task(task_func=spawn_notifications, task_param={
                "from_pleb": request.user.username,
                "sb_object": serializer['object_uuid'],
                "url": serializer['url'],
                "to_plebs": [self.kwargs[self.lookup_field], ],
                "notification_id": str(uuid1()),
                "action_name": instance.action_name
            })
            if request.query_params.get('html', 'false').lower() == "true":
                serializer['last_edited_on'] = parser.parse(
                    serializer['last_edited_on'])
                return Response(
                    {
                        "html": [render_to_string(
                            'post.html', RequestContext(request, serializer))],
                        "ids": [serializer["object_uuid"]]
                    },
                    status=status.HTTP_200_OK)
            return Response(serializer, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def post_renderer(request, username=None):
    """
    This is a intermediate step on the way to utilizing a JS Framework to
    handle template rendering.
    """
    html_array = []
    id_array = []
    posts = WallPostsListCreate.as_view()(request, username=username)
    for post in posts.data['results']:
        post['last_edited_on'] = parser.parse(post['last_edited_on'])
        html_array.append(render_to_string(
            'post.html', RequestContext(request, post)))
        id_array.append(post["object_uuid"])
    posts.data['results'] = {"html": html_array, "ids": id_array}
    return Response(posts.data, status=status.HTTP_200_OK)
