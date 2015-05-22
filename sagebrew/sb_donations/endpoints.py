from logging import getLogger

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, generics
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework import status

from neomodel import db, DoesNotExist

from api.permissions import IsOwnerOrEditorOrAccountant, IsOwnerOrAdmin
from plebs.neo_models import Pleb
from plebs.serializers import PlebSerializerNeo

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
    serializer_class = DonationSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        query = 'MATCH (c:`Campaign` {object_uuid: "%s"})-' \
                '[:RECEIVED_DONATION]-(d:`Donation`) RETURN d' % \
                (self.kwargs[self.lookup_field])
        res, col = db.cypher_query(query)
        return [Donation.inflate(row[0]) for row in res]

    @detail_route(methods=['get'], permission_classes=(
            IsAuthenticated, IsOwnerOrEditorOrAccountant))
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
