import stripe
from stripe.error import InvalidRequestError

from django.conf import settings
from django.core.cache import cache
from django.core.files.base import ContentFile

from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated, IsAdminUser)
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser

from neomodel import db

from sb_base.utils import NeoQuerySet
from api.utils import (calc_stripe_application_fee, humanize_dict_keys,
                       generate_csv_html_file_response)
from api.permissions import (IsOwnerOrAdmin, IsOwnerOrModerator,
                             IsOwnerOrEditor, IsOwnerOrModeratorOrReadOnly)

from sb_missions.neo_models import Mission
from sb_missions.serializers import MissionSerializer
from sb_donations.serializers import DonationExportSerializer
from sb_search.utils import remove_search_object
from plebs.neo_models import Pleb

from .serializers import (EditorSerializer, ModeratorSerializer,
                          PositionSerializer,
                          PositionManagerSerializer, QuestSerializer)
from .neo_models import Position, Quest


class QuestViewSet(viewsets.ModelViewSet):
    serializer_class = QuestSerializer
    lookup_field = "owner_username"
    permission_classes = (IsOwnerOrModeratorOrReadOnly,)

    def get_queryset(self):
        return NeoQuerySet(Quest)

    def get_object(self):
        return Quest.get(owner_username=self.kwargs[self.lookup_field])

    def perform_destroy(self, instance):
        # Delete all Stripe information
        # Make sure there are no pending transfers left to complete
        # TODO not sure if in_transit and pending actually work. Need to
        # test these.
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = settings.STRIPE_API_VERSION
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
                '(mission:Mission) WITH mission, r ' \
                'OPTIONAL MATCH (mission)-[r2]-() ' \
                'DELETE r, r2, mission' % instance.owner_username
        db.cypher_query(query)
        # Delete all updates associated with the Quest
        query = 'MATCH (:Quest {owner_username: "%s"})-[r:CREATED_AN]->' \
                '(update:Update) WITH r, update ' \
                'OPTIONAL MATCH (update)-[r2]-() ' \
                'DELETE r, r2, update' % instance.owner_username
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
        remove_search_object(instance.object_uuid, "quest")

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

    @detail_route(methods=['get'],
                  permission_classes=(IsAuthenticatedOrReadOnly,))
    def missions(self, request, owner_username):
        query = '(quest:Quest {owner_username: "%s"})-' \
                '[:EMBARKS_ON]->(res:Mission)' % owner_username
        if request.user.username == owner_username:
            queryset = NeoQuerySet(Mission, query=query)
        else:
            queryset = NeoQuerySet(
                Mission, query=query).filter('WHERE res.active')
        return self.get_paginated_response(
            MissionSerializer(self.paginate_queryset(queryset), many=True,
                              context={'request': request}).data)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated,
                                                       IsOwnerOrModerator,))
    def donation_data(self, request, owner_username):
        """
        This endpoint allows for the owner or accountants to get a .csv file
        containing all of the data for donations given to the mission.
        :param owner_username:
        :param request:
        :return:
        """
        self.check_object_permissions(request, owner_username)
        quest = self.get_object()
        keys = []
        donation_info = DonationExportSerializer(
            Quest.get_donations(owner_username=owner_username), many=True).data
        # this loop merges the 'owned_by' and 'address' dictionaries into
        # the top level dictionary, allows for simple writing to csv
        try:
            for donation in donation_info:
                donation.update(donation.pop('owned_by', {}))
                donation.update(donation.pop('address', {}))
                application_fee = calc_stripe_application_fee(
                    donation['amount'], quest.application_fee)
                donation['amount'] = '{:,.2f}'.format(
                    float(donation['amount'] - application_fee) / 100)
            humanized, new_keys = humanize_dict_keys(
                donation_info, donation_info[0].keys())
            # use of named temporary file here is to handle deletion of file
            # after we return the file, after the new file object is evicted
            # it gets deleted
            # http://stackoverflow.com/questions/3582414/removing-tmp-file-
            # after-return-httpresponse-in-django
            return generate_csv_html_file_response(
                "quest_donations.csv", humanized, new_keys)
        except IndexError:
            pass
        return generate_csv_html_file_response(
            "quest_donations.csv", donation_info, keys)

    @detail_route(methods=['get'], serializer_class=MissionSerializer)
    def endorsed(self, request, owner_username):
        query = 'MATCH (q:Quest {owner_username:"%s"})-' \
                '[:ENDORSES]->(m:Mission) RETURN m' % owner_username
        res, _ = db.cypher_query(query)
        page = self.paginate_queryset(
            [Mission.inflate(mission[0]) for mission in res])
        serializer = self.serializer_class(page, many=True,
                                           context={'request': request})
        return self.get_paginated_response(serializer.data)

    @detail_route(methods=['post'],
                  permission_classes=(IsAuthenticated,))
    def follow(self, request, owner_username=None):
        """
        This endpoint allows users to follow Quests.
        :param request:
        :param owner_username:
        """
        queryset = self.get_object()
        is_following = queryset.is_following(request.user.username)
        if is_following:
            return Response({"detail": "Already following user.",
                             "status": status.HTTP_200_OK},
                            status=status.HTTP_200_OK)
        queryset.follow(request.user.username)
        return Response({"detail": "Successfully followed user.",
                         "status": status.HTTP_200_OK},
                        status=status.HTTP_200_OK)

    @detail_route(methods=['post'],
                  permission_classes=(IsAuthenticated,))
    def unfollow(self, request, owner_username=None):
        """
        This endpoint allows users to unfollow Quests.
        :param request:
        :param owner_username:
        """
        queryset = self.get_object()
        is_following = queryset.is_following(request.user.username)
        if not is_following:
            return Response({"detail": "Already not following user.",
                             "status": status.HTTP_200_OK},
                            status=status.HTTP_200_OK)
        queryset.unfollow(request.user.username)
        return Response({"detail": "Successfully unfollowed user.",
                         "status": status.HTTP_200_OK},
                        status=status.HTTP_200_OK)

    @detail_route(methods=['post'],
                  permission_classes=(IsAuthenticated,),
                  parser_classes=(FormParser, MultiPartParser,))
    def upload_identification(self, request, owner_username=None):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = settings.STRIPE_API_VERSION
        return Response(request.data)
        file_object = request.data.get('img', None)
        quest = Quest.get(owner_username=owner_username)
        stripe_response = stripe.FileUpload.create(
            purpose='identity_document',
            file=ContentFile(file_object.read()),
            stripe_account=quest.stripe_customer_id
        )
        account = stripe.Account.retrieve(quest.stripe_id)
        account.legal_entity.verification.document = stripe_response['id']
        account.save()
        quest.stripe_identification_sent = True
        quest.save()
        cache.delete("%s_quest" % quest.owner_username)
        return Response({"detail": "success"}, status=status.HTTP_200_OK)


class PositionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PositionSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self, user_created='false', verified='true'):
        query = 'MATCH (p:`Position`) WHERE p.user_created=%s ' \
                'AND p.verified=%s RETURN p' % (user_created, verified)
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

    @detail_route(methods=['put', 'patch'],
                  serializer_class=PositionSerializer)
    def council_update(self, request, object_uuid=None):
        profile = Pleb.get(username=request.user.username)
        if request.user.username == "tyler_wiersing" \
                or request.user.username == "devon_bleibtrey"\
                or profile.reputation >= 10000:
            queryset = self.get_object()
            serializer = PositionSerializer(
                queryset, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"detail": "You are not authorized to perform this action.",
             "status": status.HTTP_403_FORBIDDEN},
            status.HTTP_403_FORBIDDEN)

    @list_route(methods=['get'],
                serializer_class=PositionSerializer)
    def user_created(self, request):
        queryset = self.get_queryset('true')
        return Response(PositionSerializer(queryset, many=True).data,
                        status=status.HTTP_200_OK)
