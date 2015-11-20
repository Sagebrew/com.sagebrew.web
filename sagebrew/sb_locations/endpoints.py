import urllib
from django.core.cache import cache
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

    @list_route(methods=['post'], permission_classes=(IsAuthenticated, ))
    def cache(self, request):
        if 'place_id' in request.data:
            cache.set(request.data['place_id'], request.data)
            return Response({"status": status.HTTP_201_CREATED},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"status": status.HTTP_400_BAD_REQUEST},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_positions(request, name=None):
    filter_param = request.query_params.get("filter", "")
    if filter_param == "state":
        constructed_filter = 'WHERE p.level="state_upper" ' \
                             'OR p.level="state_lower"'
    elif filter_param == '':
        constructed_filter = ''
    else:
        constructed_filter = 'WHERE p.level="%s"' % filter_param
    query = 'MATCH (l:Location {name:"%s"})-[:ENCOMPASSES*..]->' \
            '(l2:Location)-[:POSITIONS_AVAILABLE]->(p:Position) %s ' \
            'RETURN p UNION MATCH (l:Location {name:"%s"})' \
            '-[:POSITIONS_AVAILABLE]->(p:Position) %s RETURN p' \
            % (name, constructed_filter, name, constructed_filter)
    res, _ = db.cypher_query(query)
    if not res.one:
        return Response([], status=status.HTTP_200_OK)
    return Response(res, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def render_positions(request, name=None):
    return Response([render_to_string(
        'position_selector.html', {
            'name': Position.inflate(representative[0]).full_name,
            'id': Position.inflate(representative[0]).object_uuid,
            "state_name": "".join(name.split())
        }, context_instance=RequestContext(request))
        for representative in get_positions(
            request, urllib.unquote(name).decode('utf-8')).data],
        status=status.HTTP_200_OK)
