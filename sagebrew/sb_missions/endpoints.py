from rest_framework.permissions import (IsAuthenticatedOrReadOnly)

from neomodel import db
from rest_framework import viewsets

from .serializers import MissionSerializer
from .neo_models import Mission


class MissionViewSet(viewsets.ModelViewSet):
    serializer_class = MissionSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        query = 'MATCH (a:Mission) RETURN a'
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Mission.inflate(row[0]) for row in res]

    def get_object(self):
        return Mission.nodes.get(object_uuid=self.kwargs[self.lookup_field])

    def create(self, request, *args, **kwargs):
        query = 'MATCH (a:Pleb {username: "%s"})-[IS_WAGING]->(b:Quest)' \
                'RETURN b' % request.user.username
        res, _ = db.cypher_query(query)
        if res.one is None:
            self.permission_denied(request)
        return super(MissionViewSet, self).create(request, *args, **kwargs)

