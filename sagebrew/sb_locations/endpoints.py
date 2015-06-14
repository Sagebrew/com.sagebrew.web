from django.template import RequestContext
from django.template.loader import render_to_string

from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status

from neomodel import db

from sb_campaigns.neo_models import Position

from .serializers import LocationSerializer
from .neo_models import Location


class LocationList(viewsets.ReadOnlyModelViewSet):
    serializer_class = LocationSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        query = 'MATCH (l:`Location`) RETURN l'
        res, col = db.cypher_query(query)
        return [Location.inflate(row[0]) for row in res]

    def get_object(self):
        return Location.get(object_uuid=self.kwargs[self.lookup_field])


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def render_positions(request, name=None):
    query = 'MATCH (l:Location {name:"%s"})-[:POSITIONS_AVAILABLE]->' \
            '(p1:Position) WITH l, p1 OPTIONAL MATCH (l)-[:ENCOMPASSES]->' \
            '(l2:Location)-[:POSITIONS_AVAILABLE]->(p2:Position) ' \
            'RETURN p1.object_uuid as object_uuid1, ' \
            'p2.object_uuid as object_uuid2' % name
    res, _ = db.cypher_query(query)
    senator = Position.get_full_name(res[0].object_uuid1)
    house_reps = [Position.get_full_name(row.object_uuid2) for row in res]
    house_reps.append(senator)
    position_html = [render_to_string('position_selector.html',
                                      {'name': rep_name,
                                       "state_name": "".join(name.split())},
                                      context_instance=RequestContext(request))
                     for rep_name in house_reps]
    return Response(position_html, status=status.HTTP_200_OK)
