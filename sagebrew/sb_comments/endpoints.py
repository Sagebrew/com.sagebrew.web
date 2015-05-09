from uuid import uuid1
from datetime import datetime
from logging import getLogger

from django.template.loader import render_to_string
from django.template import RequestContext

from rest_framework.reverse import reverse
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (ListCreateAPIView)

from neomodel import db

from api.utils import spawn_task
from sb_base.neo_models import SBContent
from sb_base.views import ObjectRetrieveUpdateDestroy
from plebs.neo_models import Pleb

from .tasks import spawn_comment_notifications
from .neo_models import Comment
from .serializers import CommentSerializer

logger = getLogger('loggly_logs')


class ObjectCommentsRetrieveUpdateDestroy(ObjectRetrieveUpdateDestroy):
    serializer_class = CommentSerializer
    lookup_field = "object_uuid"
    lookup_url_kwarg = "comment_uuid"

    def get_object(self):
        return Comment.nodes.get(
            object_uuid=self.kwargs[self.lookup_url_kwarg])


class ObjectCommentsListCreate(ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        query = "MATCH (a:SBContent {object_uuid:'%s'})-[:HAS_A]->" \
                "(b:Comment) WHERE b.to_be_deleted=false" \
                " RETURN b ORDER BY b.created " \
                "DESC" % (self.kwargs[self.lookup_field])
        res, col = db.cypher_query(query)
        return [Comment.inflate(row[0]) for row in res]

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
            })
            html = request.query_params.get('html', 'false').lower()
            if html == "true":
                serializer_data["vote_count"] = str(
                    serializer_data["vote_count"])
                serializer_data['last_edited_on'] = datetime.strptime(
                    serializer_data['last_edited_on'][:-6],
                    '%Y-%m-%dT%H:%M:%S.%f')
                context = RequestContext(request, serializer_data)
                return Response(
                    {
                        "html": [render_to_string('comment.html', context)],
                        "ids": [serializer_data["object_uuid"]]
                    },
                    status=status.HTTP_200_OK)
            return Response(serializer_data, status=status.HTTP_200_OK)
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
        comment['last_edited_on'] = datetime.strptime(
            comment['last_edited_on'][:-6], '%Y-%m-%dT%H:%M:%S.%f')
        # This is a work around for django templates and our current
        # implementation of spacing for vote count in the template.
        comment["vote_count"] = str(comment["vote_count"])
        context = RequestContext(request, comment)
        html_array.append(render_to_string('comment.html', context))
        id_array.append(comment["object_uuid"])
    comments.data['results'] = {"html": html_array, "ids": id_array}
    return Response(comments.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def comment_list(request):
    response = {"status": status.HTTP_501_NOT_IMPLEMENTED,
                "detail": "We do not allow users to query all the comments on"
                          "the site.",
                "developer_message":
                    "We're working on enabling easier access to comments based"
                    "on user's friends and walls they have access to. "
                    "However this endpoint currently does not return any "
                    "comment data. Please use th other content endpoints to"
                    " reference the comments on them."
                }
    return Response(response, status=status.HTTP_501_NOT_IMPLEMENTED)
