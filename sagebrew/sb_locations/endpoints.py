import urllib
from django.core.cache import cache
from django.template import RequestContext
from django.template.loader import render_to_string
from django.conf import settings

from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.decorators import list_route, detail_route
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status

from neomodel import db

from sb_quests.neo_models import Position
from sb_quests.serializers import PositionSerializer

from .utils import get_positions, get_districts
from .serializers import (LocationSerializer, LocationManagerSerializer,
                          LocationExternalIDSerializer)
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
        if self.request.query_params.get('lookup', False) == "external_id":
            try:
                Location.nodes.get(external_id=self.kwargs[self.lookup_field])
            except Location.DoesNotExist:
                return None
        else:
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

    @list_route(methods=['post'],
                serializer_class=LocationExternalIDSerializer,
                permission_classes=(IsAuthenticated,))
    def async_add(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            cache.set(request.data['place_id'], request.data)
            serializer.save()
            return Response({"status": status.HTTP_201_CREATED,
                             "detail": "Successfully launched async task"},
                            status=status.HTTP_201_CREATED)
        # Don't fail loud here as we don't inform the customer that
        # we are sending off information to ourselves in the background
        return Response(serializer.errors, status=status.HTTP_200_OK)

    @list_route(methods=['post'], permission_classes=(IsAuthenticated, ))
    def cache(self, request):
        if 'place_id' in request.data:
            cache.set(request.data['place_id'], request.data)
            return Response({"status": status.HTTP_201_CREATED},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"status": status.HTTP_400_BAD_REQUEST},
                            status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'],
                  permission_classes=(IsAuthenticated,))
    def position_names(self, request, object_uuid=None):
        lookup = self.request.query_params.get('lookup', "object_uuid")
        filter_param = self.request.query_params.get('filter', "federal")
        if lookup in settings.NON_SAFE:
            return Response({"status": status.HTTP_400_BAD_REQUEST},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "results": [row[0] for row in get_positions(
                    object_uuid, filter_param=filter_param, lookup=lookup,
                    distinct=True, property_name=".name")],
                "status": status.HTTP_200_OK
            }, status=status.HTTP_200_OK)

    @detail_route(methods=['get'],
                  permission_classes=(IsAuthenticated,))
    def positions(self, request, object_uuid=None):
        lookup = self.request.query_params.get('lookup', "object_uuid")
        filter_param = self.request.query_params.get('filter')
        if lookup in settings.NON_SAFE:
            return Response({"status": status.HTTP_400_BAD_REQUEST},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "results": [PositionSerializer(Position.inflate(row[0])).data
                            for row in get_positions(object_uuid,
                                                     filter_param=filter_param,
                                                     lookup=lookup)],
                "status": status.HTTP_200_OK
            }, status=status.HTTP_200_OK)

    @detail_route(methods=['get'],
                  permission_classes=(IsAuthenticated,))
    def district_names(self, request, object_uuid=None):
        lookup = self.request.query_params.get('lookup', "object_uuid")
        filter_param = self.request.query_params.get('filter', "federal")
        if lookup in settings.NON_SAFE:
            return Response({"status": status.HTTP_400_BAD_REQUEST},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "results": [row[0] for row in get_districts(
                    object_uuid, filter_param=filter_param, lookup=lookup,
                    distinct=True, property_name=".name")],
                "status": status.HTTP_200_OK
            }, status=status.HTTP_200_OK)

    @detail_route(methods=['get'],
                  permission_classes=(IsAuthenticated,))
    def districts(self, request, object_uuid=None):
        lookup = self.request.query_params.get('lookup', "object_uuid")
        filter_param = self.request.query_params.get('filter', "federal")
        if lookup in settings.NON_SAFE:
            return Response({"status": status.HTTP_400_BAD_REQUEST},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "results": [LocationSerializer(
                    Location.inflate(row[0])).data for row in get_districts(
                        object_uuid, filter_param=filter_param, lookup=lookup)],
                "status": status.HTTP_200_OK
            }, status=status.HTTP_200_OK)


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
            urllib.unquote(name).decode('utf-8'),
            request.query_params.get("filter", ""))],
        status=status.HTTP_200_OK)
