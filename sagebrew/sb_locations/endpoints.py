from django.core.cache import cache
from django.conf import settings

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
        query = 'MATCH (l:Location) RETURN l'
        res, col = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Location.inflate(row[0]) for row in res]

    def get_object(self):
        lookup_value = self.request.query_params.get('lookup', 'object_uuid')
        if lookup_value != "object_uuid" and lookup_value != "external_id" \
                and lookup_value != "name":
            lookup_value = "object_uuid"
        if lookup_value == "name":
            query_id = self.kwargs[self.lookup_field].title()
        else:
            query_id = self.kwargs[self.lookup_field]
        query = 'MATCH (location:Location {%s: "%s"}) RETURN location' % (
            lookup_value, query_id)
        res, _ = db.cypher_query(query)
        if res.one:
            return Location.inflate(res.one)
        else:
            return None

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
    def add_external_id(self, request):
        serializer = self.get_serializer(data=request.data,
                                         context={'request': request})
        if serializer.is_valid():
            response = serializer.save()
            if response is not None:
                return Response({"status": status.HTTP_201_CREATED,
                                 "detail": "Successfully created location id"},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST,
                                 "detail": "Unable to access that location"},
                                status=status.HTTP_400_BAD_REQUEST)
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
