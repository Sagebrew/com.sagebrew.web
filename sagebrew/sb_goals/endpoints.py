from logging import getLogger
from django.template.loader import render_to_string

from rest_framework.decorators import (api_view, permission_classes)

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework import status, generics, viewsets
from neomodel import db

from api.permissions import IsGoalOwnerOrEditor
from sb_campaigns.neo_models import Campaign

from .serializers import (GoalSerializer, RoundSerializer)
from .neo_models import Goal, Round

logger = getLogger('loggly_logs')


class GoalListCreateMixin(generics.ListCreateAPIView):
    """
    This mixin is utilized at the campaign endpoint. This allows us to get a
    list of all goals attached to a campaign. This will return a serialized
    list of goals for the given campaign.

    You must give this view the uuid of the campaign you wish to see the goals
    of.
    """
    # to view the current and past goals
    serializer_class = GoalSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        query = "MATCH (c:`Campaign` {object_uuid:'%s'})-[:HAS_ROUND]->" \
                "(r:`Round`)-[:STRIVING_FOR]->(g:`Goal`) RETURN g " \
                % (self.kwargs[self.lookup_field])
        res, col = db.cypher_query(query)
        return [Goal.inflate(row[0]) for row in res]

    def perform_create(self, serializer):
        serializer.save(campaign=Campaign.get(self.kwargs[self.lookup_field]))

    def create(self, request, *args, **kwargs):
        if not (request.user.username in
                Campaign.get_editors(self.kwargs[self.lookup_field])):
            return Response({"status_code": status.HTTP_403_FORBIDDEN,
                             "detail": "Authentication credentials were "
                                       "not provided."},
                            status=status.HTTP_403_FORBIDDEN)
        html = request.query_params.get('html', 'false')
        if html == 'true':
            instance = super(GoalListCreateMixin, self).create(request, *args,
                                                               **kwargs)
            return Response(render_to_string('goal_draggable.html',
                                             instance.data),
                            status=status.HTTP_200_OK)
        return super(GoalListCreateMixin, self).create(request, *args,
                                                       **kwargs)


class GoalRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView,
                                viewsets.GenericViewSet):
    serializer_class = GoalSerializer
    permission_classes = (IsAuthenticated, IsGoalOwnerOrEditor)
    lookup_field = "object_uuid"

    def get_object(self):
        return Goal.nodes.get(object_uuid=self.kwargs[self.lookup_field])

    def perform_update(self, serializer):
        serializer.save(prev_goal=self.request.data.get('prev_goal', None),
                        campaign=self.request.data.get('campaign', None))

    def update(self, request, *args, **kwargs):
        """
        Overwriting update here to provide for a custom validation of updating
        goals. Doing the validation here means that we do not have to modify
        our custom exception handling methods. If we did this validation in
        the update method of the serializer we would have to overwrite the
        way that validation errors are handled.
        """
        queryset = self.get_object()
        if queryset.completed is True or queryset.active is True:
            return Response({"status_code": status.HTTP_405_METHOD_NOT_ALLOWED,
                             "detail": "You cannot update a completed "
                                       "or active goal."},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super(GoalRetrieveUpdateDestroy, self).update(request,
                                                             *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        queryset = self.get_object()
        if queryset.completed is True or queryset.active is True:
            return Response({"status_code": status.HTTP_405_METHOD_NOT_ALLOWED,
                             "detail": "You cannot delete a completed "
                                       "or active goal."},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super(GoalRetrieveUpdateDestroy, self).destroy(request, *args,
                                                              **kwargs)

    @detail_route(methods=['PUT', 'PATCH'], serializer_class=GoalSerializer,
                  permission_classes=(IsAuthenticated, IsGoalOwnerOrEditor))
    def disconnect_round(self, request, object_uuid=None):
        queryset = self.get_object()
        if queryset.completed is True or queryset.active is True:
            return Response({"status_code": status.HTTP_405_METHOD_NOT_ALLOWED,
                             "detail": "You cannot modify a completed "
                                       "or active goal."},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        queryset.disconnect_from_upcoming()
        return Response({"status_code": status.HTTP_200_OK,
                         "detail": "Successfully removed goal from upcoming "
                                   "round."},
                        status=status.HTTP_200_OK)




class RoundListCreate(generics.ListCreateAPIView):
    """
    This mixin allows for us to get a list of all the rounds that have ever
    been associated with a campaign.

    You must give this view the uuid of the campaign you wish to see the
    rounds of.
    """
    serializer_class = RoundSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        query = "MATCH (c:`Campaign` {object_uuid:'%s'})-" \
                "[:HAS_ROUND]->(r:`Round`) RETURN r" % \
                (self.kwargs[self.lookup_field])
        res, col = db.cypher_query(query)
        return [Round.inflate(row[0]) for row in res]


class RoundRetrieve(generics.RetrieveAPIView):
    serializer_class = RoundSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"

    def get_object(self):
        return Round.nodes.get(object_uuid=self.kwargs[self.lookup_field])

    def get(self, request, *args, **kwargs):
        queryset = self.get_object()
        if queryset.completed is None and queryset.active is False:
            if not (request.user.username in
                    Campaign.get_campaign_helpers(Round.get_campaign(
                        queryset.object_uuid))):
                return Response({"detail": "Only owners, editors, or "
                                           "accountants can view upcoming "
                                           "rounds.",
                                 "status_code": status.HTTP_401_UNAUTHORIZED},
                                status=status.HTTP_401_UNAUTHORIZED)
        return super(RoundRetrieve, self).get(request, *args, **kwargs)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def render_round_goals(request, object_uuid=None):
    query = 'MATCH (r:Round {object_uuid: "%s"})-[:STRIVING_FOR]->(g:Goal) ' \
            'RETURN g ORDER BY g.total_required' % object_uuid
    res, _ = db.cypher_query(query)
    html = [render_to_string('goal_draggable.html',
                             GoalSerializer(Goal.inflate(row[0])).data)
            for row in res]
    return Response(html, status=status.HTTP_200_OK)

