from uuid import uuid1

from rest_framework.reverse import reverse
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (ListCreateAPIView)
from rest_framework.exceptions import NotAuthenticated

from neomodel import db

from api.utils import spawn_task
from sb_base.neo_models import SBContent
from sb_base.views import ObjectRetrieveUpdateDestroy
from plebs.neo_models import Pleb

from .tasks import spawn_comment_notifications
from .neo_models import Comment
from .serializers import CommentSerializer


class ObjectCommentsRetrieveUpdateDestroy(ObjectRetrieveUpdateDestroy):
    serializer_class = CommentSerializer
    lookup_field = "object_uuid"
    lookup_url_kwarg = "comment_uuid"
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_object(self):
        obj = Comment.nodes.get(
            object_uuid=self.kwargs[self.lookup_url_kwarg])
        if obj.visibility == "private":
            # TODO restrict comments to only be shown to users who follow the
            # owner
            if self.request.user.is_authenticated():
                return obj
            else:
                raise NotAuthenticated
        return obj


class ObjectCommentsListCreate(ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        if self.request.user.is_authenticated():
            query = "MATCH (a:SBContent {object_uuid:'%s'})-[:HAS_A]->" \
                    "(b:Comment) WHERE b.to_be_deleted=false" \
                    " RETURN b ORDER BY b.created DESC" % (
                        self.kwargs[self.lookup_field])
            res, _ = db.cypher_query(query)
        else:
            query = "MATCH (a:SBContent {object_uuid:'%s'})-[:HAS_A]->" \
                    "(b:Comment) WHERE a.visibility='public' AND" \
                    " b.to_be_deleted=false" \
                    " RETURN b ORDER BY b.created DESC" % (
                        self.kwargs[self.lookup_field])
            res, _ = db.cypher_query(query)
        return res

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        page = page[::-1]
        [row[0].pull() for row in page]
        page = [Comment.inflate(row[0]) for row in page]
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            pleb = Pleb.get(request.user.username)
            parent_object = SBContent.nodes.get(
                object_uuid=self.kwargs[self.lookup_field])
            instance = serializer.save(owner=pleb, parent_object=parent_object)
            serializer_data = serializer.data
            serializer_data['comment_on'] = reverse(
                '%s-detail' % parent_object.get_child_label().lower(),
                kwargs={'object_uuid': parent_object.object_uuid},
                request=request)
            serializer_data['url'] = parent_object.get_url(request=request)
            notification_id = str(uuid1())
            spawn_task(task_func=spawn_comment_notifications, task_param={
                'from_pleb': request.user.username,
                'parent_object_uuid': self.kwargs[self.lookup_field],
                'object_uuid': instance.object_uuid,
                'notification_id': notification_id,
                'comment_on_comment_id': str(uuid1())
            })
            return Response(serializer_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def comment_list(request):
    response = {"status": status.HTTP_501_NOT_IMPLEMENTED,
                "detail": "We do not allow users to query all the comments on"
                          " the site.",
                "developer_message":
                    "We're working on enabling easier access to comments based"
                    "on user's friends and walls they have access to. "
                    "However this endpoint currently does not return any "
                    "comment data. Please use th other content endpoints to"
                    " reference the comments on them."
                }
    return Response(response, status=status.HTTP_501_NOT_IMPLEMENTED)
