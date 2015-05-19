from logging import getLogger

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework import status

from neomodel import db, DoesNotExist

from api.permissions import IsOwnerOrEditorOrAccountant, IsOwnerOrAdmin
from plebs.neo_models import Pleb
from plebs.serializers import PlebSerializerNeo

from .neo_models import Donation
from .serializers import DonationSerializer


class DonationViewSet(viewsets.ModelViewSet):
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
        return [Donation.inflate(row[0]) for row in res][0]