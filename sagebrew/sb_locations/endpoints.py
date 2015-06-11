from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status

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


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def render_positions(request, name=None):
    from logging import getLogger
    logger = getLogger('loggly_logs')
    query = 'MATCH (l:Location {name:"%s"})-[:POSITIONS_AVAILABLE]->' \
            '(p1:Position) WITH l, p1 OPTIONAL MATCH (l)-[:ENCOMPASSES]->' \
            '(l2:Location)-[:POSITIONS_AVAILABLE]->(p2:Position)' \
            'RETURN p1, p2' % name
    res, _ = db.cypher_query(query)
    logger.info(res)
    return Response(res, status=status)
