import csv

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.core.files.temp import NamedTemporaryFile
from django.core.servers.basehttp import FileWrapper
from django.template.loader import render_to_string
from django.templatetags.static import static

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework import status

from neomodel import db
from elasticsearch import Elasticsearch

from api.permissions import (IsOwnerOrAdmin, IsOwnerOrAccountant,
                             IsOwnerOrEditor)
from sb_goals.serializers import GoalSerializer
from sb_donations.neo_models import Donation
from sb_donations.serializers import DonationExportSerializer
from plebs.serializers import PlebSerializerNeo
from plebs.neo_models import Pleb

from .serializers import (CampaignSerializer, PoliticalCampaignSerializer,
                          EditorSerializer, AccountantSerializer,
                          PositionSerializer, PoliticalVoteSerializer)
from .neo_models import Campaign, PoliticalCampaign, Position

from logging import getLogger
logger = getLogger('loggly_logs')


class CampaignViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        query = "MATCH (c:`Campaign`) RETURN c"
        res, col = db.cypher_query(query)
        try:
            return [Campaign.inflate(row[0]) for row in res]
        except IndexError:
            return []

    def get_object(self):
        return Campaign.get(object_uuid=self.kwargs[self.lookup_field])

    def perform_update(self, serializer):
        serializer.save(stripe_token=self.request.data.get('stripe_token',
                                                           None),
                        ein=self.request.data.get('ein', None),
                        ssn=self.request.data.get('ssn', None))

    @detail_route(methods=['get'],
                  permission_classes=(IsAuthenticated, IsOwnerOrEditor))
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
        queryset = Campaign.get_editors(object_uuid)
        html = request.query_params.get('html', 'false').lower()
        if html == 'true':
            queryset.remove(object_uuid)
            return Response({"ids": queryset, "html": [
                render_to_string("current_editor.html",
                                 PlebSerializerNeo(Pleb.get(pleb)).data)
                for pleb in queryset]}, status=status.HTTP_200_OK)
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
        serializer = self.get_serializer(self.get_object(), data=request.data)
        html = request.query_params.get('html', 'false').lower()
        if serializer.is_valid():
            serializer.save()
            if html == 'true':
                return Response(
                    {"ids": serializer.validated_data['profiles'],
                     "html": [render_to_string("current_editor.html",
                                               PlebSerializerNeo(
                                                   Pleb.get(pleb)).data)
                              for pleb in
                              serializer.validated_data['profiles']]},
                    status=status.HTTP_200_OK)
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
        html = request.query_params.get('html', 'false').lower()
        if serializer.is_valid():
            # The profiles key here refers to a list of usernames
            # not the actual user objects
            serializer.remove_profiles(queryset)
            if html == 'true':
                return Response({"ids": serializer.data['profiles'], "html": [
                    render_to_string("potential_campaign_helper.html",
                                     PlebSerializerNeo(Pleb.get(pleb)).data)
                    for pleb in serializer.data['profiles']]},
                    status=status.HTTP_200_OK)
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
        serializer = self.get_serializer(self.get_object(), data=request.data)
        html = request.query_params.get('html', 'false').lower()
        if serializer.is_valid():
            serializer.save()
            if html == 'true':
                return Response({"ids": serializer.validated_data['profiles'],
                                 "html": [render_to_string(
                                     "current_accountant.html",
                                     PlebSerializerNeo(Pleb.get(pleb)).data)
                                     for pleb
                                     in serializer.validated_data[
                                     'profiles']]},
                                status=status.HTTP_200_OK)
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
        html = request.query_params.get('html', 'false').lower()
        if serializer.is_valid():
            serializer.remove_profiles(queryset)
            if html == 'true':
                return Response({"ids": serializer.data['profiles'], "html": [
                    render_to_string("potential_campaign_helper.html",
                                     PlebSerializerNeo(Pleb.get(pleb)).data)
                    for pleb in serializer.data['profiles']]},
                    status=status.HTTP_200_OK)
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
        html = request.query_params.get('html', 'false').lower()
        queryset = Campaign.get_accountants(object_uuid)
        if html == 'true':
            queryset.remove(object_uuid)
            return Response({"ids": queryset, "html": [
                render_to_string("current_accountant.html",
                                 PlebSerializerNeo(Pleb.get(pleb)).data)
                for pleb in queryset]}, status=status.HTTP_200_OK)
        return Response(queryset, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated,
                                                       IsOwnerOrAccountant,))
    def donation_data(self, request, object_uuid=None):
        """
        This endpoint allows for the owner or accountants to get a .csv file
        containing all of the data for donations given to the campaign.

        :param request:
        :param object_uuid:
        :return:
        """
        self.check_object_permissions(request, object_uuid)
        donation_info = [DonationExportSerializer(
            Donation.inflate(donation)).data for donation in
                         Campaign.get_donations(object_uuid)]
        # this loop merges the 'owned_by' and 'address' dictionaries into
        # the top level dictionary, allows for simple writing to csv

        try:
            for donation in donation_info:
                donation.update(donation.pop('owned_by', {}))
                donation.update(donation.pop('address', {}))
            keys = donation_info[0].keys()
            # use of named temporary file here is to handle deletion of file
            # after we return the file, after the new file object is evicted
            # it gets deleted
            # http://stackoverflow.com/questions/3582414/removing-tmp-file-after-return-httpresponse-in-django
            newfile = NamedTemporaryFile(suffix='.csv')
            newfile.name = "%s_quest_donations.csv" % object_uuid
            dict_writer = csv.DictWriter(newfile, keys)
            dict_writer.writeheader()
            dict_writer.writerows(donation_info)
            # the HttpResponse use here allows us to do an automatic download
            # upon hitting the button
            httpresponse = HttpResponse(FileWrapper(newfile),
                                        content_type="text/csv")
            httpresponse['Content-Disposition'] = 'attachment; filename=%s' \
                                                  % newfile.name
            return httpresponse
        except IndexError:
            return Response({'detail': 'Unable to find any donation data',
                             'status_code':
                                 status.HTTP_404_NOT_FOUND},
                            status=status.HTTP_404_NOT_FOUND)


class PoliticalCampaignViewSet(CampaignViewSet):
    serializer_class = PoliticalCampaignSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        query = "MATCH (c:`PoliticalCampaign`) RETURN c"
        res, col = db.cypher_query(query)
        try:
            return [PoliticalCampaign.inflate(row[0]) for row in res]
        except IndexError:
            return []

    def get_object(self):
        return PoliticalCampaign.get(self.kwargs[self.lookup_field])

    def perform_create(self, serializer):
        instance = serializer.save(position=Position.nodes.get(
            object_uuid=self.request.data['position']))
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        es.index(index='full-search-base', doc_type=serializer.data['type'],
                 id=serializer.data['id'], body=serializer.data)
        return instance

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        serializer_data = dict(serializer.data)
        if serializer_data['wallpaper_pic'] is None:
            serializer_data['wallpaper_pic'] = static(
                'images/wallpaper_capitol_2.jpg')
        if serializer_data['profile_pic'] is None:
            serializer_data['profile_pic'] = static(
                'images/sage_coffee_grey-01.png')
        return Response(serializer_data)

    def update(self, request, *args, **kwargs):
        if not (request.user.username in Campaign.get_editors
                (self.kwargs[self.lookup_field])):
            return Response({"status_code": status.HTTP_403_FORBIDDEN,
                             "detail": "You are not authorized to access "
                                       "this page."},
                            status=status.HTTP_403_FORBIDDEN)
        return super(PoliticalCampaignViewSet, self).update(request, *args,
                                                            **kwargs)

    @detail_route(methods=['post'], serializer_class=PoliticalVoteSerializer)
    def vote(self, request, object_uuid=None):
        serializer = self.get_serializer(data=request.data,
                                         context={"request": request})
        if serializer.is_valid():
            cache.delete("%s_vote_count" % (object_uuid))
            parent_object_uuid = self.kwargs[self.lookup_field]
            res = PoliticalCampaign.vote_campaign(parent_object_uuid,
                                                  request.user.username)
            if res:
                return Response({"detail": res,
                                 "status": status.HTTP_200_OK,
                                 "developer_message": None},
                                status=status.HTTP_200_OK)
            return Response({"detail": "Successfully unpledged vote.",
                             "status": status.HTTP_200_OK,
                             "developer_message": None})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated,
                                                       IsOwnerOrAccountant,),
                  serializer_class=PoliticalVoteSerializer)
    def pledged_votes(self, request, object_uuid=None):
        queryset = self.get_object().get_pledged_votes()
        serializer_data = self.get_serializer(queryset, many=True).data
        return Response(serializer_data, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], serializer_class=GoalSerializer)
    def unassigned_goals(self, request, object_uuid=None):
        if not (request.user.username in Campaign.get_editors
                (self.kwargs[self.lookup_field])):
            return Response({"status_code": status.HTTP_403_FORBIDDEN,
                             "detail": "You are not authorized to access "
                                       "this page."},
                            status=status.HTTP_403_FORBIDDEN)
        html = request.query_params.get('html', 'false').lower()
        queryset = PoliticalCampaign.get_unassigned_goals(object_uuid)
        if html == 'true':
            return Response([render_to_string(
                "goal_draggable.html", GoalSerializer(goal).data)
                for goal in queryset], status=status.HTTP_200_OK)
        return Response(self.serializer_class(queryset, many=True).data,
                        status=status.HTTP_200_OK)

    @detail_route(methods=['get'], serializer_class=PlebSerializerNeo)
    def possible_helpers(self, request, object_uuid=None):
        if not request.user.username == object_uuid:
            return Response({"status_code": status.HTTP_403_FORBIDDEN,
                             "detail": "You are not authorized to access "
                                       "this page."},
                            status=status.HTTP_403_FORBIDDEN)
        html = request.query_params.get('html', 'false').lower()
        queryset = PoliticalCampaign.get_possible_helpers(object_uuid)
        if html == 'true':
            return Response({"ids": queryset,
                             "html": [
                                 render_to_string(
                                     'potential_campaign_helper.html',
                                     PlebSerializerNeo(Pleb.get(pleb)).data)
                                 for pleb in queryset]},
                            status=status.HTTP_200_OK)
        return Response(self.serializer_class(queryset, many=True).data,
                        status=status.HTTP_200_OK)


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
