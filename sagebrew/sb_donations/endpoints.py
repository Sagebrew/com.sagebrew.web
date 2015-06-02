from logging import getLogger

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, generics
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework import status

from neomodel import db, DoesNotExist

from api.permissions import IsOwnerOrEditorOrAccountant, IsOwnerOrAccountant, IsOwnerOrAdmin
from plebs.neo_models import Pleb
from plebs.serializers import PlebSerializerNeo
from sb_campaigns.neo_models import Campaign
from sb_goals.neo_models import Goal

from .neo_models import Donation
from .serializers import DonationSerializer

logger = getLogger('loggly_logs')


class DonationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DonationSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        query = 'MATCH (d:`Donation` {object_uuid: "%s"}) RETURN d' % \
                (self.kwargs[self.lookup_field])
        res, col = db.cypher_query(query)
        return Donation.inflate(res[0][0])

    def list(self, request, *args, **kwargs):
        return Response({'detail': "Sorry, we currently do not allow for "
                                   "users to query all donations for every "
                                   "campaign.",
                         'status_code': status.HTTP_405_METHOD_NOT_ALLOWED},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, *args, **kwargs):
        if (request.user.username ==
                Donation.get_owner(self.kwargs[self.lookup_field])):
            return super(DonationViewSet, self).retrieve(request, *args,
                                                         **kwargs)
        return Response({"detail": "Sorry only the owner of a donation is "
                                   "allowed to see its detail page.",
                         "status_code": status.HTTP_403_FORBIDDEN},
                        status=status.HTTP_403_FORBIDDEN)

class DonationListCreate(generics.ListCreateAPIView):
    """
    This endpoint will be utilized to allow accountants of a campaign to view
    the donations attached to the campaign. Also allows users to create
    donations on this endpoint. We set up some custom validation for the
    list method to only allow the owner or an accountant to view a list of
    donations attached to the campaign.
    """
    serializer_class = DonationSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        query = 'MATCH (c:`Campaign` {object_uuid: "%s"})-' \
                '[:RECEIVED_DONATION]->(d:`Donation`) RETURN d' % \
                (self.kwargs[self.lookup_field])
        res, col = db.cypher_query(query)
        return [Donation.inflate(row[0]) for row in res]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            campaign = Campaign.get(object_uuid=self.kwargs[self.lookup_field])
            donated_towards = [Goal.nodes.get(object_uuid=goal) for goal in
                               request.data.get('donated_towards', [])]
            serializer.save(campaign=campaign, donated_towards=donated_towards)
            return Response({"detail": "Successfully created donation.",
                             "status_code": status.HTTP_200_OK},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        if not (request.user.username in Campaign.get_accountants
                (self.kwargs[self.lookup_field])):
            return Response({"status_code": status.HTTP_403_FORBIDDEN,
                             "detail": "You are not authorized to access "
                                       "this page."},
                            status=status.HTTP_403_FORBIDDEN)
        return super(DonationListCreate, self).list(request, *args, **kwargs)
