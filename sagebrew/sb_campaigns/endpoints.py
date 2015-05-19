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

from .serializers import (CampaignSerializer, PoliticalCampaignSerializer,
                          EditorAccountantSerializer, PositionSerializer)
from .neo_models import Campaign, PoliticalCampaign, Position

logger = getLogger('loggly_logs')


class CampaignViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        query = "MATCH (c:`Campaign`) RETURN c"
        res, col = db.cypher_query(query)
        return [Campaign.inflate(row[0]) for row in res]

    def get_object(self):
        return Campaign.nodes.get(
            object_uuid=self.kwargs[self.lookup_field])

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data,
                                         context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_object()
        return Response(self.get_serializer(queryset,
                                            context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @detail_route(methods=['get'],
                  permission_classes=(IsAuthenticated,
                                      IsOwnerOrEditorOrAccountant))
    def editors(self, request, object_uuid=""):
        editor_list = []
        query = 'MATCH (c:`Campaign` {object_uuid: "%s"})-' \
                '[:CAN_BE_EDITED_BY]-(p:`Pleb`) RETURN p' % (object_uuid)
        res, col = db.cypher_query(query)
        editors = [Pleb.inflate(row[0]) for row in res]
        #self.check_object_permissions(request, queryset)
        for editor in editors:
            editor_info = editor.username
            editor_info = PlebSerializerNeo(
                editor, context={'request': request}).data
            editor_list.append(editor_info)
        return Response(editor_list, status=status.HTTP_200_OK)

    @detail_route(methods=['post'],
                  serializer_class=EditorAccountantSerializer,
                  permission_classes=(IsAuthenticated, IsOwnerOrAdmin,))
    def add_editors(self, request, *args, **kwargs):
        """
        This method will take a list of usernames which will be added to the
        editors of the campaign. Only to be used to add a list of editors to
        the campaign. We are not fully modifying the list we are just adding
        to it.

        :param request:
        :return:
        """
        queryset = self.get_object()
        self.check_object_permissions(request, queryset)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile_type="editor",
                            modification_type="add",
                            single_object=queryset)
            return Response({"detail": "success",
                             "message": "Successfully added specified users "
                                        "to your campaign editors."},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'],
                  serializer_class=EditorAccountantSerializer,
                  permission_classes=(IsAuthenticated, IsOwnerOrAdmin,))
    def remove_editors(self, request, *args, **kwargs):
        """
        This is a method which will only be used to remove the users
        in the list posted to this endpoint from the list of allowed editors
        of the campaign.

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        queryset = self.get_object()
        self.check_object_permissions(request, queryset)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile_type="editor",
                            modification_type="delete",
                            single_object=queryset)
            return Response({"detail": "success",
                             "message": "Successfully removed specified "
                                        "editors from your campaign."},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'],
                  serializer_class=EditorAccountantSerializer,
                  permission_classes=(IsAuthenticated, IsOwnerOrAdmin,))
    def add_accountants(self, request, *args, **kwargs):
        """
        This helper method will take a list of usernames which are to be added
        to the list of accountants for the campaign and create the necessary
        connections.

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        queryset = self.get_object()
        self.check_object_permissions(request, queryset)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile_type="accountant",
                            modification_type="add",
                            single_object=queryset)
            return Response({"detail": "success",
                             "message": "Successfully added specified users to"
                                        " your campaign accountants."},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'],
                  serializer_class=EditorAccountantSerializer,
                  permission_classes=(IsAuthenticated, IsOwnerOrAdmin,))
    def remove_accountants(self, request, *args, **kwargs):
        """
        This helper method will take a list of usernames which are to be
        removed from the list of accountants for the campaign and remove
        the connections.

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        queryset = self.get_object()
        self.check_object_permissions(request, queryset)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile_type="accountant",
                            modification_type="delete",
                            single_object=queryset)
            return Response({"detail": "success",
                             "message": "Successfully removed specified "
                                        "accountants from your campaign."},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated,
                                      IsOwnerOrEditorOrAccountant,))
    def accountants(self, request, *args, **kwargs):
        accountant_list = []
        queryset = self.get_object()
        self.check_object_permissions(request, queryset)
        expand = request.query_params.get('expand', 'false').lower()
        accountants = queryset.accountants.all()
        for accountant in accountants:
            accountant_info = accountant.username
            if expand == 'true':
                accountant_info = PlebSerializerNeo(
                    accountant, context={'request': request}).data
            accountant_list.append(accountant_info)
        return Response(accountant_list, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], serializer_class=PositionSerializer)
    def position(self, request, *args, **kwargs):
        query = "MATCH (c:`Campaign`)--(p:`Position`) RETURN p"
        res, col = db.cypher_query(query)
        position = [Position.inflate(row[0]) for row in res][0]
        return Response(self.get_serializer(position,
                                            context={'request': request}).data,
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
        return PoliticalCampaign.nodes.get(
            object_uuid=self.kwargs[self.lookup_field])

    @detail_route(methods=['get'])
    def votes(self, request, *args, **kwargs):
        pass

    @detail_route(methods=['get'])
    def vote_count(self, request, *args, **kwargs):
        pass
