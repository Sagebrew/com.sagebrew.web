from datetime import datetime
from logging import getLogger

from django.template.loader import render_to_string
from django.template import RequestContext

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework import status, generics

from neomodel import db

from api.utils import spawn_task
from sb_base.utils import get_ordering, get_tagged_as
from sb_stats.tasks import update_view_count_task
from plebs.neo_models import Pleb
from plebs.serializers import PlebSerializerNeo

from .serializers import (CampaignSerializer, PoliticalCampaignSerializer,
                          DonationSerializer, UpdateSerializer,
                          PledgeVoteSerializer, GoalSerializer)
from .neo_models import Campaign, PoliticalCampaign


class PoliticalCampaignViewSet(viewsets.ModelViewSet):
    serializer_class = PoliticalCampaignSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return PoliticalCampaign.nodes.all()

    def get_object(self):
        return PoliticalCampaign.nodes.get(
            object_uuid=self.kwargs[self.lookup_field])

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data,
                                         context={"request": request})
        if serializer.is_valid():
            serializer.save()
            serializer = serializer.data
            return Response(serializer, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_object()
        single_object = CampaignSerializer(
            queryset, context={'request': request}).data

        return Response(single_object, status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def editors(self, request, *args, **kwargs):
        editor_list = []
        queryset = self.get_object()
        expand = request.query_params.get('expand', 'false').lower()
        editors = queryset.editors.all()
        for editor in editors:
            editor_info = editor.username
            if expand == 'true':
                editor_info = PlebSerializerNeo(
                    editor, context={'request': request}).data
            editor_list.append(editor_info)
        return Response(editor_list, status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
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
        new_editors = request.data['new_editors']
        for editor in new_editors:
            editor_pleb = Pleb.get(username=editor)
            if queryset.editors.is_connected(editor_pleb):
                continue
            queryset.editors.connect(editor_pleb)
            editor_pleb.campaign_editor.connect(queryset)
        return Response({"detail": "success",
                         "message": "Successfully added all editors "
                                    "to your campaign"},
                        status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def delete_editors(self, request, *args, **kwargs):
        """
        This is a method which will only be used to remove the users
        in the list posted to this endpoint from the list of allowed editors
        of the campaign.

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        pass

    @detail_route(methods=['get'])
    def accountants(self, request, *args, **kwargs):
        accountant_list = []
        queryset = self.get_object()
        expand = request.query_params.get('expand', 'false').lower()
        accountants = queryset.accountants.all()
        for accountant in accountants:
            accountant_info = accountant.username
            if expand == 'true':
                accountant_info = PlebSerializerNeo(
                    accountant, context={'request': request}).data
            accountant_list.append(accountant_info)
        return accountant_list

    @detail_route(methods=['get'])
    def goals(self, request, *args, **kwargs):
        pass

    @detail_route(methods=['get'])
    def updates(self, request, *args, **kwargs):
        pass

    @detail_route(methods=['get'])
    def rounds(self, request, *args, **kwargs):
        pass


class DonationViewSet(viewsets.ModelViewSet):
    serializer_class = PoliticalCampaignSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)
