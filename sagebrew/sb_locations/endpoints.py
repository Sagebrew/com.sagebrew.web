from logging import getLogger

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, generics
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework import status

from neomodel import db, DoesNotExist

from api.permissions import IsOwnerOrEditorOrAccountant, IsOwnerOrAdmin
from plebs.neo_models import Pleb
from plebs.serializers import PlebSerializerNeo

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
        return Location.nodes.get(object_uuid=self.kwargs[self.lookup_field])

