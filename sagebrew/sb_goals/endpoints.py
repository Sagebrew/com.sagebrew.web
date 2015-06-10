from logging import getLogger

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics

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

    def create(self, request, *args, **kwargs):
        if not (request.user.username in
                Campaign.get_editors(self.kwargs[self.lookup_field])):
            return Response({"status_code": status.HTTP_403_FORBIDDEN,
                             "detail": "Authentication credentials were "
                                       "not provided."},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            campaign = Campaign.get(self.kwargs[self.lookup_field])
            serializer.save(campaign=campaign)
            return Response({"detail": "Successfully created goal.",
                             "status_code": status.HTTP_200_OK})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoalRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GoalSerializer
    permission_classes = (IsAuthenticated, IsGoalOwnerOrEditor)
    lookup_field = "object_uuid"

    def get_object(self):
        return Goal.nodes.get(object_uuid=self.kwargs[self.lookup_field])

    def update(self, request, *args, **kwargs):
        """
        Overwriting update here to provide for a custom validation of updating
        goals. Doing the validation here means that we do not have to modify
        our custom exception handling methods. If we did this validation in
        the update method of the serializer we would have to overwrite the
        way that validation errors are handled.
        """
        queryset = self.get_object()
        if (queryset.completed or queryset.active):
            return Response({"status_code": status.HTTP_405_METHOD_NOT_ALLOWED,
                             "detail": "You cannot update a completed "
                                       "or active goal."},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super(GoalRetrieveUpdateDestroy, self).update(request,
                                                             *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        queryset = self.get_object()
        if (queryset.completed or queryset.active):
            return Response({"status_code": status.HTTP_405_METHOD_NOT_ALLOWED,
                             "detail": "You cannot delete a completed "
                                       "or active goal."},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super(GoalRetrieveUpdateDestroy, self).destroy(request, *args,
                                                              **kwargs)


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
