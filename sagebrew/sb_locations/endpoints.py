from django.template import RequestContext
from django.template.loader import render_to_string

from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status

from neomodel import db

from sb_quests.neo_models import Position

from .serializers import LocationSerializer, LocationManagerSerializer
from .neo_models import Location


class LocationList(viewsets.ReadOnlyModelViewSet):
    serializer_class = LocationSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        query = 'MATCH (l:`Location`) RETURN l'
        res, col = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Location.inflate(row[0]) for row in res]

    def get_object(self):
        return Location.get(object_uuid=self.kwargs[self.lookup_field])

    @list_route(methods=['post'],
                serializer_class=LocationManagerSerializer,
                permission_classes=(IsAdminUser,))
    def add(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer = serializer.save()
            return Response(LocationSerializer(serializer).data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_positions(request, name=None):
    from logging import getLogger
    logger = getLogger('loggly_logs')
    filter_param = request.query_params.get('filter')
    constructed_filter = ''
    query = 'MATCH (l:Location {name:"%s"})-[:ENCOMPASSES*..]->' \
            '(l2:Location) WITH collect(id(l))+collect(id(l2)) ' \
            'AS collected_ids OPTIONAL MATCH (final_location:Location)-' \
            '[:POSITIONS_AVAILABLE]->' \
            '(p:Position) WHERE id(final_location) in collected_ids %s ' \
            'RETURN collect(DISTINCT p.object_uuid) as uuids' \
            % (name, constructed_filter)
    res, _ = db.cypher_query(query)
    if not res.one:
        return Response([], status=status.HTTP_200_OK)
    return Response(res[0].uuids, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def render_positions(request, name=None):
    return Response([render_to_string(
        'position_selector.html', {
            'name': Position.get_full_name(
                representative),
            "state_name": "".join(name.split())
        }, context_instance=RequestContext(request))
        for representative in get_positions(request, name).data],
        status=status.HTTP_200_OK)
