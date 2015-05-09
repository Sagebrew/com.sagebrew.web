from dateutil import parser
from logging import getLogger

from django.template.loader import render_to_string
from django.template import RequestContext

from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (ListAPIView, RetrieveAPIView)

from neomodel import db

from .neo_models import Notification
from .serializers import NotificationSerializer

logger = getLogger('loggly_logs')


class UserNotificationRetrieve(RetrieveAPIView):
    """
    This endpoint assumes it is placed on a specific user endpoint where
    it can really on the currently logged in user to gather notifications
    for. It is not capable of being set on an arbitrary user's profile
    endpoint like other method endpoints we have.
    """
    serializer_class = NotificationSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated, )

    def get_object(self):
        return Notification.nodes.get(
            object_uuid=self.kwargs[self.lookup_field])


class UserNotificationList(ListAPIView):
    """
    This endpoint assumes it is placed on a specific user endpoint where
    it can really on the currently logged in user to gather notifications
    for. It is not capable of being set on an arbitrary user's profile
    endpoint like other method endpoints we have.
    """
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        query = 'MATCH (a:Pleb {username: "%s"})-[:RECEIVED_A]->' \
                '(n:Notification) WHERE n.seen=false RETURN n ORDER ' \
                'BY n.created DESC LIMIT 7' % (self.request.user.username)
        res, col = db.cypher_query(query)
        return [Notification.inflate(row[0]) for row in res]


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def notification_renderer(request, object_uuid=None):
    """
    This is a intermediate step on the way to utilizing a JS Framework to
    handle template rendering.
    """
    html_array = []
    id_array = []
    args = []
    kwargs = {"object_uuid": object_uuid}
    notifications = UserNotificationList.as_view()(request, *args, **kwargs)
    for notification in notifications.data['results']:
        notification['time_sent'] = parser.parse(notification['time_sent'])
        context = RequestContext(request, notification)
        html_array.append(render_to_string('general_notification_block.html',
                                           context))
        id_array.append(notification["object_uuid"])
    notifications.data['results'] = {"html": html_array, "ids": id_array}
    return Response(notifications.data, status=status.HTTP_200_OK)
