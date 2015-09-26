from dateutil import parser

from django.template.loader import render_to_string
from django.template import RequestContext
from django.core.cache import cache

from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (ListAPIView, RetrieveAPIView)

from neomodel import db

from .neo_models import Notification
from .serializers import NotificationSerializer


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
        notifications = cache.get("%s_notifications" % (
            self.request.user.username))
        if notifications is None:
            query = 'MATCH (a:Pleb {username: "%s"})-[:RECEIVED_A]->' \
                '(n:Notification) RETURN n ORDER ' \
                'BY n.created DESC LIMIT 5' % self.request.user.username
            res, col = db.cypher_query(query)
            [row[0].pull() for row in res]
            notifications = [Notification.inflate(row[0]) for row in res]
            cache.set("%s_notifications" % self.request.user.username,
                      notifications)
        return notifications

    def list(self, request, *args, **kwargs):
        """
        Had to overwrite this function to add a check for a query param being
        passed that when set to true will set all the user's current
        notifications to seen
        """
        seen = request.query_params.get('seen', 'false').lower()
        if seen == "true":
            Notification.clear_unseen(request.user.username)
            # Set queryset to [] as this query param means they've already
            # loaded the initial queryset and just want to mark them as
            # seen
            queryset = []
        else:
            queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


@api_view(["GET"])
@permission_classes((IsAuthenticated, ))
def notification_renderer(request, object_uuid=None):
    """
    This is a intermediate step on the way to utilizing a JS Framework to
    handle template rendering.
    """
    html_array = []
    id_array = []
    notifications = UserNotificationList.as_view()(request)
    for notification in notifications.data.get('results', []):
        notification['time_sent'] = parser.parse(notification['time_sent'])
        context = RequestContext(request, notification)
        html_array.append(render_to_string('general_notification_block.html',
                                           context))
        id_array.append(notification["id"])

    notifications.data['results'] = {
        "html": html_array, "ids": id_array,
        "unseen": Notification.unseen(request.user.username)
    }
    return Response(notifications.data, status=status.HTTP_200_OK)
