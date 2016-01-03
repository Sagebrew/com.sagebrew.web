from api.permissions import (IsOwnerOrModeratorOrReadOnly)

from neomodel import db
from rest_framework import viewsets

from .serializers import MissionSerializer
from .neo_models import Mission


class MissionViewSet(viewsets.ModelViewSet):
    serializer_class = MissionSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsOwnerOrModeratorOrReadOnly,)

    def get_queryset(self):
        if self.request.query_params.get('affects', "") == "me":
            query = 'MATCH (pleb:Pleb {username: "%s"})-[:LIVES_AT]->' \
                    '(address:Address)-[:ENCOMPASSED_BY*..]->' \
                    '(location:Location)<-[:WITHIN]-' \
                    '(mission:Mission {active: true}) ' \
                    'RETURN DISTINCT mission' % self.request.user.username
        elif self.request.query_params.get('affects', "") == "friends":
            query = 'MATCH (pleb:Pleb {username: "%s"})-[:FRIENDS_WITH]' \
                    '->(friends:Pleb)-[:LIVES_AT]->' \
                    '(address:Address)-[:ENCOMPASSED_BY*..]->' \
                    '(location:Location)<-[:WITHIN]-' \
                    '(mission:Mission {active: true}) ' \
                    'RETURN DISTINCT mission' % self.request.user.username
        else:
            query = 'MATCH (a:Mission {active: true}) RETURN a'
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
