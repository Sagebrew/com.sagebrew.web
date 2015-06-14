import pytz
from datetime import datetime

from django.core.cache import cache

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework import status

from neomodel import db

from api.permissions import (IsOwnerOrAdmin, IsOwnerOrAccountant,
                             IsOwnerOrEditor)
from sb_votes.utils import handle_vote

from .serializers import (CampaignSerializer, PoliticalCampaignSerializer,
                          EditorSerializer, AccountantSerializer,
                          PositionSerializer, PoliticalVoteSerializer)
from .neo_models import Campaign, PoliticalCampaign, Position


class CampaignViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        query = "MATCH (c:`Campaign`) RETURN c"
        res, col = db.cypher_query(query)
        return [Campaign.inflate(row[0]) for row in res]

    def get_object(self):
        return Campaign.get(object_uuid=self.kwargs[self.lookup_field])

    @detail_route(methods=['get'],
                  permission_classes=(IsAuthenticated,
                                      IsOwnerOrEditor))
    def editors(self, request, object_uuid=None):
        """
        This is a method on the endpoint because there should be no reason
        for people other than the owner or editors to view the editors of
        the page. We want to keep this information private so that no one
        other than someone who is associated with the campaign knows who has
        access to edit the campaign.

        :param request:
        :param object_uuid:
        :return:
        """
        self.check_object_permissions(request, object_uuid)
        return Response(Campaign.get_editors(object_uuid),
                        status=status.HTTP_200_OK)

    @detail_route(methods=['post'],
                  serializer_class=EditorSerializer,
                  permission_classes=(IsAuthenticated, IsOwnerOrAdmin,))
    def add_editors(self, request, object_uuid=None):
        """
        This method will take a list of usernames which will be added to the
        editors of the campaign. Only to be used to add a list of editors to
        the campaign. We are not fully modifying the list we are just adding
        to it.

        :param request:
        :return:
        """
        serializer = self.get_serializer(self.get_object(),
                                         data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Successfully added specified users "
                                       "to your campaign.",
                             "status": status.HTTP_200_OK,
                             "developer_message": None},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'],
                  serializer_class=EditorSerializer,
                  permission_classes=(IsAuthenticated, IsOwnerOrAdmin,))
    def remove_editors(self, request, object_uuid=None):
        """
        This is a method which will only be used to remove the users
        in the list posted to this endpoint from the list of allowed editors
        of the campaign.

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        queryset = self.get_object()
        if serializer.is_valid():
            # The profiles key here refers to a list of usernames
            # not the actual user objects
            serializer.remove_profiles(queryset)
            return Response({"detail": "Successfully removed specified "
                                       "editors from your campaign.",
                             "status": status.HTTP_200_OK,
                             "developer_message": None},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'],
                  serializer_class=AccountantSerializer,
                  permission_classes=(IsAuthenticated, IsOwnerOrAdmin,))
    def add_accountants(self, request, object_uuid=None):
        """
        This helper method will take a list of usernames which are to be added
        to the list of accountants for the campaign and create the necessary
        connections.

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(self.get_object(),
                                         data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Successfully added specified users to"
                                       " your campaign accountants.",
                             "status": status.HTTP_200_OK,
                             "developer_message": None},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'],
                  serializer_class=AccountantSerializer,
                  permission_classes=(IsAuthenticated, IsOwnerOrAdmin,))
    def remove_accountants(self, request, object_uuid=None):
        """
        This helper method will take a list of usernames which are to be
        removed from the list of accountants for the campaign and remove
        the connections.

        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        serializer = self.get_serializer(data=request.data)
        queryset = self.get_object()
        if serializer.is_valid():
            serializer.remove_profiles(queryset)
            return Response({"detail": "Successfully removed specified "
                                       "accountants from your campaign.",
                             "status": status.HTTP_200_OK,
                             "developer_message": None},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated,
                                                       IsOwnerOrAccountant,))
    def accountants(self, request, object_uuid=None):
        """
        This is a method on the endpoint because there should be no reason
        for people other than the owner or accountants to view the accountants
        of the page. We want to keep this information private so that no one
        other than someone who is associated with the campaign knows who has
        access to modify the campaign.

        :param request:
        :param object_uuid:
        :return:
        """
        self.check_object_permissions(request, object_uuid)
        return Response(Campaign.get_accountants(object_uuid),
                        status=status.HTTP_200_OK)


class PoliticalCampaignViewSet(CampaignViewSet):
    serializer_class = PoliticalCampaignSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        query = "MATCH (c:`PoliticalCampaign`) RETURN c"
        res, col = db.cypher_query(query)
        return [PoliticalCampaign.inflate(row[0]) for row in res]

    def get_object(self):
        return PoliticalCampaign.get(self.kwargs[self.lookup_field])

    def perform_create(self, serializer):
        instance = serializer.save(position=Position.nodes.get(
            object_uuid=self.request.data['position']))
        return instance

    @detail_route(methods=['post'], serializer_class=PoliticalVoteSerializer)
    def vote(self, request, object_uuid=None):
        serializer = self.get_serializer(data=request.data,
                                         context={"request": request})
        if serializer.is_valid():
            cache.delete("%s_vote_count" % (object_uuid))
            parent_object_uuid = self.kwargs[self.lookup_field]
            now = unicode(datetime.now(pytz.utc))
            res = handle_vote(parent_object_uuid, serializer.data['vote_type'],
                              request, now)
            if res:
                return Response({"detail": "Successfully pledged vote.",
                                 "status": status.HTTP_200_OK,
                                 "developer_message": None},
                                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PositionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PositionSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        query = 'MATCH (p:`Position`) RETURN p'
        res, col = db.cypher_query(query)
        return [Position.inflate(row[0]) for row in res]

    def get_object(self):
        return Position.get(self.kwargs[self.lookup_field])
