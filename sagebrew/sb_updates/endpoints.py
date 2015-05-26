from dateutil import parser

from django.template.loader import render_to_string
from django.template import RequestContext

from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status

from neomodel import db

from sb_base.views import ObjectRetrieveUpdateDestroy

from .serializers import UpdateSerializer
from .neo_models import Update


class UpdateListCreate(generics.ListCreateAPIView):
    serializer_class = UpdateSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        query = 'MATCH (c:`Campaign` {object_uuid:"%s"})-' \
                '[:HAS_UPDATE]-(u:`Update`) return u' % \
                (self.kwargs[self.lookup_field])
        res, col = db.cypher_query(query)
        return [Update.inflate(row[0]) for row in res]

    def get_object(self):
        return Update.nodes.get(object_uuid=self.kwargs[self.lookup_field])

class UpdateRetrieveUpdateDestroy(ObjectRetrieveUpdateDestroy):
    serializer_class = UpdateSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return Update.nodes.get(object_uuid=self.kwargs[self.lookup_field])


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def update_renderer(request, object_uuid=None):
    html_array = []
    id_array = []
    args = []
    kwargs = {"object_uuid": object_uuid}
    updates = UpdateListCreate.as_view()(request, *args, **kwargs)
    for update in updates.data['results']:
        update['last_edited_on'] = parser.parse(update['last_edited_on'])
        update['vote_count'] = str(update['vote_count'])
        context = RequestContext(request, update)
        # TODO make a template for updates
        html_array.append(render_to_string('update.html', context))
        id_array.append(update['object_uuid'])
    updates.data['results'] = {'html': html_array, 'ids': id_array}
    return Response(updates.data, status=status.HTTP_200_OK)
