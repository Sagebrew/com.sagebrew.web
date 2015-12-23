import csv
import stripe
from stripe.error import InvalidRequestError

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.core.files.temp import NamedTemporaryFile
from django.core.servers.basehttp import FileWrapper
from django.template.loader import render_to_string
from django.templatetags.static import static

from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated, IsAdminUser)
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework import status

from neomodel import db
from elasticsearch import Elasticsearch

from api.permissions import (IsOwnerOrAdmin, IsOwnerOrModerator,
                             IsOwnerOrEditor, IsOwnerOrModeratorOrReadOnly)
from sb_goals.serializers import GoalSerializer
from sb_donations.neo_models import Donation
from sb_donations.serializers import DonationExportSerializer
from plebs.serializers import PlebSerializerNeo
from plebs.neo_models import Pleb

from .serializers import (CampaignSerializer, PoliticalCampaignSerializer,
                          EditorSerializer, ModeratorSerializer,
                          PositionSerializer,
                          PositionManagerSerializer, QuestSerializer,
                          AccountantSerializer)
from .neo_models import Campaign, PoliticalCampaign, Position, Quest


class QuestViewSet(viewsets.ModelViewSet):
    serializer_class = QuestSerializer
    lookup_field = "owner_username"
    permission_classes = (IsOwnerOrModeratorOrReadOnly,)

    def get_queryset(self):
        query = "MATCH (c:Quest) RETURN c"
        res, col = db.cypher_query(query)
        try:
            [row[0].pull() for row in res]
            return [Quest.inflate(row[0]) for row in res]
        except IndexError:
            return []

    def get_object(self):
        return Quest.get(owner_username=self.kwargs[self.lookup_field])

    def perform_destroy(self, instance):
        # Delete all Stripe information
        # Make sure there are no pending transfers left to complete
        # TODO not sure if in_transit and pending actually work. Need to
        # test these.
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            in_transit = stripe.Transfer.all(recipient=instance.stripe_id,
                                             status="in_transit")
            if len(in_transit['data']) > 0:
                raise ValidationError(
                    detail={"detail": "Sorry you cannot delete your Quest "
                                      "while there are donations in "
                                      "transit. Please deactivate your "
                                      "Quest if it isn't already and "
                                      "wait for all donations to complete.",
                            "status_code": status.HTTP_400_BAD_REQUEST})
        except InvalidRequestError:
            pass
        try:
            pending = stripe.Transfer.all(recipient=instance.stripe_id,
                                          status="pending")
            if len(pending['data']) > 0:
                raise ValidationError(
                    detail={"detail": "Sorry you cannot delete your Quest "
                                      "while there are donations pending. "
                                      "Please deactivate your Quest if it "
                                      "isn't already and wait for all "
                                      "donations to complete.",
                            "status_code": status.HTTP_400_BAD_REQUEST})
        except InvalidRequestError:
            pass
        # Delete credit card info associated with a Quest that had a
        # subscription
        if instance.stripe_customer_id is not None:
            customer = stripe.Customer.retrieve(instance.stripe_customer_id)
            if instance.stripe_subscription_id is not None:
                customer.subscriptions.retrieve(
                    instance.stripe_subscription_id).delete()
            try:
                customer.delete()
            except InvalidRequestError:
                # appears the customer has already been deleted
                pass
        # Delete the managed account associated with a Quest.
        if instance.stripe_id is not None and instance.stripe_id != "Not Set":
            account = stripe.Account.retrieve(instance.stripe_id)
            try:
                account.delete()
            except InvalidRequestError:
                # appears the account has already been deleted
                pass
        # Clear the cache of all missions that the Quest has
        query = 'MATCH (:Quest {owner_username: "%s"})-[r:EMBARKS_ON]->' \
                '(mission:Mission) ' \
                'RETURN mission.object_uuid' % instance.owner_username
        res, _ = db.cypher_query(query)
        if res.one is not None:
            [cache.delete("%s_mission" % mission) for mission in res.one]
        # Delete all missions associated with the Quest
        query = 'MATCH (:Quest {owner_username: "%s"})-[r:EMBARKS_ON]->' \
                '(mission:Mission)-[r2]-() ' \
                'DELETE r, r2, mission' % instance.owner_username
        db.cypher_query(query)
        # Delete all updates associated with the Quest
        query = 'MATCH (:Quest {owner_username: "%s"})-[r:CREATED_AN]->' \
                '(update:Update) ' \
                'DELETE r, update' % instance.owner_username
        db.cypher_query(query)
        # Delete all endorsements associated with the Quest
        query = 'MATCH (:Quest {owner_username: "%s"})-[r:ENDORSES]->' \
                '(:Mission) ' \
                'DELETE r' % instance.owner_username
        db.cypher_query(query)
        # Delete all other relationships and the quest itself
        query = 'MATCH (quest:Quest {owner_username: "%s"})-[r]-() ' \
                'DELETE r, quest' % instance.owner_username
        db.cypher_query(query)
        cache.delete("%s_moderators" % instance.owner_username)
        cache.delete("%s_editors" % instance.owner_username)
        cache.delete("%s_moderators" % instance.owner_username)
        cache.delete("%s_quest" % instance.owner_username)

    @detail_route(methods=['get'],
                  permission_classes=(IsAuthenticated, IsOwnerOrEditor))
    def editors(self, request, owner_username=None):
        """
        This is a method on the endpoint because there should be no reason
        for people other than the owner or editors to view the editors of
        the page. We want to keep this information private so that no one
        other than someone who is associated with the campaign knows who has
        access to edit the campaign.

        :param request:
        :param owner_username:
        :return:
        """
        self.check_object_permissions(request, owner_username)
        return Response(Quest.get_editors(owner_username),
                        status=status.HTTP_200_OK)

    @detail_route(methods=['put'],
                  serializer_class=EditorSerializer,
                  permission_classes=(IsAuthenticated, IsOwnerOrAdmin,))
    def add_editors(self, request, owner_username=None):
        """
        This method will take a list of usernames which will be added to the
        editors of the campaign. Only to be used to add a list of editors to
        the campaign. We are not fully modifying the list we are just adding
        to it.

        :param owner_username:
        :param request:
        :return:
        """
        serializer = self.get_serializer(self.get_object(), data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Successfully added specified users "
                                       "to your quest.",
                             "status": status.HTTP_200_OK,
                             "developer_message": None},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['put'],
                  serializer_class=EditorSerializer,
                  permission_classes=(IsAuthenticated, IsOwnerOrAdmin,))
    def remove_editors(self, request, owner_username=None):
        """
        This is a method which will only be used to remove the users
        in the list posted to this endpoint from the list of allowed editors
        of the campaign.

        :param request:
        :param owner_username:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        queryset = self.get_object()
        if serializer.is_valid():
            # The profiles key here refers to a list of usernames
            # not the actual user objects
            serializer.remove_profiles(queryset)
            return Response({"detail": "Successfully removed specified "
                                       "editors from your quest.",
                             "status": status.HTTP_200_OK,
                             "developer_message": None},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['put'],
                  serializer_class=ModeratorSerializer,
                  permission_classes=(IsAuthenticated, IsOwnerOrAdmin,))
    def add_moderators(self, request, owner_username=None):
        """
        This helper method will take a list of usernames which are to be added
        to the list of accountants for the campaign and create the necessary
        connections.

        :param request:
        :param owner_username:
        :return:
        """
        serializer = self.get_serializer(self.get_object(), data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Successfully added specified users to"
                                       " your quest moderators.",
                             "status": status.HTTP_200_OK,
                             "developer_message": None},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['put'],
                  serializer_class=ModeratorSerializer,
                  permission_classes=(IsAuthenticated, IsOwnerOrAdmin,))
    def remove_moderators(self, request, owner_username=None):
        """
        This helper method will take a list of usernames which are to be
        removed from the list of accountants for the campaign and remove
        the connections.

        :param request:
        :param owner_username:
        :return:
        """

        serializer = self.get_serializer(data=request.data)
        queryset = self.get_object()
        if serializer.is_valid():
            serializer.remove_profiles(queryset)
            return Response({"detail": "Successfully removed specified "
                                       "moderators from your quest.",
                             "status": status.HTTP_200_OK,
                             "developer_message": None},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated,
                                                       IsOwnerOrModerator,))
    def moderators(self, request, owner_username=None):
        """
        This is a method on the endpoint because there should be no reason
        for people other than the owner or accountants to view the accountants
        of the page. We want to keep this information private so that no one
        other than someone who is associated with the campaign knows who has
        access to modify the campaign.

        :param owner_username:
        :param request:
        :return:
        """
        self.check_object_permissions(request, owner_username)
        return Response(Quest.get_moderators(owner_username),
                        status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated,
                                                       IsOwnerOrModerator,))
    def donation_data(self, request, owner_username=None):
        """
        This endpoint allows for the owner or accountants to get a .csv file
        containing all of the data for donations given to the campaign.

        :param request:
        :param owner_username:
        :return:
        """
        self.check_object_permissions(request, owner_username)
        donation_info = [DonationExportSerializer(
            Donation.inflate(donation)).data for donation in
            Quest.get_donations(owner_username)]
        campaign = self.get_object()
        # this loop merges the 'owned_by' and 'address' dictionaries into
        # the top level dictionary, allows for simple writing to csv
        try:
            for donation in donation_info:
                donation.update(donation.pop('owned_by', {}))
                donation.update(donation.pop('address', {}))
                application_fee = donation['amount'] * (
                    campaign.application_fee +
                    settings.STRIPE_TRANSACTION_PERCENT) + .3
                donation['amount'] -= application_fee
            keys = []
            for key in donation_info[0].keys():
                new_key = key.replace('_', ' ').title()
                for donation in donation_info:
                    donation[new_key] = donation[key]
                    donation.pop(key, None)
                keys.append(new_key)
            # use of named temporary file here is to handle deletion of file
            # after we return the file, after the new file object is evicted
            # it gets deleted
            # http://stackoverflow.com/questions/3582414/removing-tmp-file-after-return-httpresponse-in-django
            newfile = NamedTemporaryFile(suffix='.csv', delete=False)
            newfile.name = "%s_quest_donations.csv" % owner_username
            dict_writer = csv.DictWriter(newfile, keys)
            dict_writer.writeheader()
            dict_writer.writerows(donation_info)
            # the HttpResponse use here allows us to do an automatic download
            # upon hitting the button
            newfile.seek(0)
            wrapper = FileWrapper(newfile)
            httpresponse = HttpResponse(wrapper,
                                        content_type="text/csv")
            httpresponse['Content-Disposition'] = 'attachment; filename=%s' \
                                                  % newfile.name
            return httpresponse
        except IndexError:
            return Response({'detail': 'Unable to find any donation data',
                             'status_code':
                                 status.HTTP_404_NOT_FOUND},
                            status=status.HTTP_404_NOT_FOUND)


class CampaignViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        query = "MATCH (c:`Campaign`) RETURN c"
        res, col = db.cypher_query(query)
        try:
            [row[0].pull() for row in res]
            return [Campaign.inflate(row[0]) for row in res]
        except IndexError:
            return []

    def get_object(self):
        return Campaign.get(object_uuid=self.kwargs[self.lookup_field])

    def perform_update(self, serializer):
        serializer.save(stripe_token=self.request.data.get('stripe_token',
                                                           None),
                        customer_token=self.request.data.get('customer_token',
                                                             None),
                        ein=self.request.data.get('ein', None),
                        ssn=self.request.data.get('ssn', None),
                        activate=self.request.data.get('activate', None))

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
                    render_to_string("potential_quest_helper.html",
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
                                       " your quest moderators.",
                             "status": status.HTTP_200_OK,
                             "developer_message": None},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PoliticalCampaignViewSet(CampaignViewSet):
    serializer_class = PoliticalCampaignSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        query = "MATCH (c:`PoliticalCampaign`) RETURN c"
        res, col = db.cypher_query(query)
        try:
            [row[0].pull() for row in res]
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
        if not (request.user.username in
                Campaign.get_campaign_helpers(
                    self.kwargs[self.lookup_field])):
            return Response({"status_code": status.HTTP_403_FORBIDDEN,
                             "detail": "You are not authorized to access "
                                       "this page."},
                            status=status.HTTP_403_FORBIDDEN)
        return super(PoliticalCampaignViewSet, self).update(request, *args,
                                                            **kwargs)

    @detail_route(methods=['get'], serializer_class=GoalSerializer)
    def unassigned_goals(self, request, object_uuid=None):
        if not (request.user.username in
                Campaign.get_campaign_helpers(
                    self.kwargs[self.lookup_field])):
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
                                     'potential_quest_helper.html',
                                     PlebSerializerNeo(Pleb.get(pleb)).data)
                                 for pleb in queryset]},
                            status=status.HTTP_200_OK)
        return Response(self.serializer_class(queryset, many=True).data,
                        status=status.HTTP_200_OK)


class PositionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PositionSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        query = 'MATCH (p:`Position`) RETURN p'
        res, col = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Position.inflate(row[0]) for row in res]

    def get_object(self):
        return Position.get(self.kwargs[self.lookup_field])

    @list_route(methods=['post'],
                serializer_class=PositionManagerSerializer,
                permission_classes=(IsAdminUser,))
    def add(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer = serializer.save()
            return Response(PositionSerializer(serializer).data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
