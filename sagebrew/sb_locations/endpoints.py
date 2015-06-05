from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from neomodel import db

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
