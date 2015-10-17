from uuid import uuid1
from dateutil import parser

from django.template.loader import render_to_string
from django.template import RequestContext

from rest_framework.reverse import reverse
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import (IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status

from neomodel import db

from sb_base.views import ObjectRetrieveUpdateDestroy
from sb_quests.neo_models import Campaign
from sb_goals.neo_models import Goal

from .serializers import UpdateSerializer
from .neo_models import Update


class UpdateListCreate(generics.ListCreateAPIView):
    serializer_class = UpdateSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        query = 'MATCH (c:`Campaign` {object_uuid:"%s"})-' \
                '[:HAS_UPDATE]->(u:`Update`) return u ' \
                'ORDER BY u.created DESC' % \
                (self.kwargs[self.lookup_field])
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Update.inflate(row[0]) for row in res]

    def get_object(self):
        return Update.nodes.get(object_uuid=self.kwargs[self.lookup_field])

    def perform_create(self, serializer):
        # updates can only be attached to any of the currently active goals,
        # completed or not
        object_uuid = str(uuid1())
        serializer.save(
            campaign=Campaign.get(object_uuid=self.kwargs[self.lookup_field]),
            associated_goals=self.request.data.get('goals', []),
            url=reverse('quest_updates', kwargs={
                'username': self.request.user.username}, request=self.request),
            object_uuid=object_uuid,
            href=reverse('update-detail', kwargs={'object_uuid': object_uuid},
                         request=self.request)
        )

    def create(self, request, *args, **kwargs):
        if not (request.user.username in
                Campaign.get_editors(self.kwargs[self.lookup_field])
                or request.user.username in
                Campaign.get_accountants(self.kwargs[self.lookup_field])):
            return Response({"status_code": status.HTTP_403_FORBIDDEN,
                             "detail": "You are not authorized to access "
                                       "this page."},
                            status=status.HTTP_403_FORBIDDEN)
        return super(UpdateListCreate, self).create(request, *args, **kwargs)


class UpdateRetrieveUpdateDestroy(ObjectRetrieveUpdateDestroy):
    serializer_class = UpdateSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_object(self):
        return Update.nodes.get(object_uuid=self.kwargs[self.lookup_field])

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "Sorry we do not allow deletion of updates.",
             "status_code": status.HTTP_405_METHOD_NOT_ALLOWED},
            status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
def update_renderer(request, object_uuid=None):
    html_array = []
    id_array = []
    args = []
    kwargs = {"object_uuid": object_uuid}
    updates = UpdateListCreate.as_view()(request, *args, **kwargs)
    for update in updates.data['results']:
        update['last_edited_on'] = parser.parse(
            update['last_edited_on']).replace(microsecond=0)
        update['created'] = parser.parse(
            update['created']).replace(microsecond=0)
        update['vote_count'] = str(update['vote_count'])
        update['goals'] = ", ".join([Goal.nodes.get(object_uuid=goal).title
                                    for goal in update['goals']])

        context = RequestContext(request, update)
        html_array.append(render_to_string('update.html', context))
        id_array.append(update['object_uuid'])
    updates.data['results'] = {'html': html_array, 'ids': id_array}
    return Response(updates.data, status=status.HTTP_200_OK)
