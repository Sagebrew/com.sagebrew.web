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


class GoalListMixin(generics.ListAPIView):
    """
    This mixin is utilized at the campaign endpoint. This allows us to get a
    list of all goals attached to a campaign. This will return a serialized
    list of goals for the given campaign.

    You must give this view the uuid of the campaign you wish to see the goals
    of.
    """
    # TODO add custom functionality to only allow the owner or editor of a
    # campaign to add a goal to the campaign. We can use the logic that we
    # used in sb_donations.endpoints just reversed to allow anyone to see
    # goals and only editors to create goals
    # TODO look in to only allowing users other than owner/editors/accountants
    # to view the current and past goals
    serializer_class = GoalSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        query = "MATCH (r:`Campaign` {object_uuid:'%s'})-[:HAS_ROUND]->" \
                "(r:`Round`)-[:STRIVING_FOR]->(g:`Goal`) RETURN g " \
                "ORDER BY g.created" % (self.kwargs[self.lookup_field])
        res, col = db.cypher_query(query)
        return [Goal.inflate(row[0]) for row in res]


class RoundListCreate(generics.ListCreateAPIView):
    """
    This mixin allows for us to get a list of all the rounds that have ever
    been associated with a campaign.

    You must give this view the uuid of the campaign you wish to see the
    rounds of.
    """
    # TODO add custom functionality to only allow the owner or editor of a
    # campaign to add a round to the campaign. We can use the logic that we
    # used in sb_donations.endpoints just reversed to allow anyone to see
    # rounds and only editors to create rounds
    # TODO look in to only allowing users other than owner/editors/accountants
    # to view the current and past rounds
    serializer_class = RoundSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        query = "MATCH (c:`Campaign` {object_uuid:'%s'})-" \
                "[:HAS_ROUND]->(r:`Round`) RETURN r" % \
                (self.kwargs[self.lookup_field])
        res, col = db.cypher_query(query)
        return [Round.inflate(row[0]) for row in res]
