from datetime import datetime
from logging import getLogger

from django.template.loader import render_to_string
from django.template import RequestContext

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework import status, generics

from neomodel import db, DoesNotExist

from api.utils import spawn_task
from api.permissions import IsOwnerOrEditorOrAccountant, IsOwnerOrAdmin
from sb_base.utils import get_ordering, get_tagged_as
from sb_stats.tasks import update_view_count_task
from plebs.neo_models import Pleb
from plebs.serializers import PlebSerializerNeo
from sb_campaigns.neo_models import Campaign

from .serializers import (GoalSerializer, RoundSerializer)
from .neo_models import Goal, Round

logger = getLogger('loggly_logs')


class GoalListMixin(generics.ListCreateAPIView):
    serializer_class = GoalSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        query = "MATCH (r:`Round` {object_uuid:'%s'})-[:STRIVING_FOR]->" \
                "(g:`Goal`) WHERE g.to_be_delete=false RETURN g " \
                "ORDER BY g.created" % (self.kwargs[self.lookup_field])
        res, col = db.cypher_query(query)
        return [Goal.inflate(row[0]) for row in res]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            query = "MATCH (c:`Campaign`)-[:HAS_ROUND]->" \
                    "(r:`Round`{object_uuid:'%s'}) RETURN c, r"
            res, col = db.cypher_query(query)
            campaign = [Campaign.inflate(row[0]) for row in res][0]
            campaign_round = [Round.inflate(row[1]) for row in res][0]
            serializer.save(campaign=campaign, round=campaign_round)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        pass


class RoundViewSet(generics.ListCreateAPIView):
    serializer_class = RoundSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        query = "MATCH (r:`Round`{object_uuid:'%s'}) RETURN r"
        res, col = db.cypher_query(query)
        return [Round.inflate(row[0]) for row in res]
