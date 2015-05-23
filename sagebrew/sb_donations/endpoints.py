from logging import getLogger

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, generics
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework import status

from neomodel import db, DoesNotExist

from api.permissions import IsOwnerOrEditorOrAccountant, IsOwnerOrAccountant
from plebs.neo_models import Pleb
from plebs.serializers import PlebSerializerNeo
from sb_campaigns.neo_models import Campaign

from .neo_models import Donation
from .serializers import DonationSerializer


class DonationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DonationSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        query = "MATCH (d:`Donation`) RETURN d"
        res, col = db.cypher_query(query)
        return [Donation.inflate(row[0]) for row in res]

    def get_object(self):
        query = 'MATCH (d:`Donation` {object_uuid: "%s"}) RETURN d'
        res, col = db.cypher_query(query)
        return Donation.inflate(res[0][0])

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
                '[:RECEIVED_DONATION]-(d:`Donation`) RETURN d' % \
                (self.kwargs[self.lookup_field])
        res, col = db.cypher_query(query)
        return [Donation.inflate(row[0]) for row in res]

    def list(self, request, *args, **kwargs):
        if not (request.user.username in Campaign.get_accountants
                (self.kwargs[self.lookup_field])):
            return Response({"status_code": status.HTTP_403_FORBIDDEN,
                             "detail": "Authentication credentials were "
                                       "not provided."})
        return super(DonationListCreate, self).list(request, *args, **kwargs)


