import pytz
from datetime import datetime
import time
import stripe
import markdown

from django.conf import settings
from django.core.cache import cache

from rest_framework import serializers, status
from rest_framework.reverse import reverse
from rest_framework.exceptions import ValidationError

from neomodel import db
from neomodel.exception import DoesNotExist

from api.serializers import SBSerializer
from api.utils import gather_request_data, spawn_task
from plebs.neo_models import Pleb
from sb_goals.neo_models import Round, Goal
from sb_public_official.serializers import PublicOfficialSerializer
from sb_privileges.tasks import check_privileges
from sb_locations.neo_models import Location

from .neo_models import (Campaign, PoliticalCampaign, Position)

from logging import getLogger
logger = getLogger('loggly_logs')


class CampaignSerializer(SBSerializer):
    active = serializers.BooleanField(required=False, read_only=True)
    biography = serializers.CharField(required=False, max_length=255)
    epic = serializers.CharField(required=False, allow_blank=True)
    facebook = serializers.CharField(required=False, allow_blank=True)
    linkedin = serializers.CharField(required=False, allow_blank=True)
    youtube = serializers.CharField(required=False, allow_blank=True)
    twitter = serializers.CharField(required=False, allow_blank=True)
    website = serializers.CharField(required=False, allow_blank=True)
    wallpaper_pic = serializers.CharField(required=False)
    profile_pic = serializers.CharField(required=False)
    owner_username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    location_name = serializers.CharField(read_only=True)
    position_name = serializers.CharField(read_only=True)
    position_formal_name = serializers.CharField(read_only=True)

    url = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()
    rounds = serializers.SerializerMethodField()
    updates = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()
    is_editor = serializers.SerializerMethodField()
    reputation = serializers.SerializerMethodField()
    active_goals = serializers.SerializerMethodField()
    active_round = serializers.SerializerMethodField()
    is_accountant = serializers.SerializerMethodField()
    rendered_epic = serializers.SerializerMethodField()
    upcoming_round = serializers.SerializerMethodField()
    public_official = serializers.SerializerMethodField()
    completed_stripe = serializers.SerializerMethodField()
    completed_customer = serializers.SerializerMethodField()
    total_donation_amount = serializers.SerializerMethodField()
    total_pledge_vote_amount = serializers.SerializerMethodField()
    target_goal_donation_requirement = serializers.SerializerMethodField()
    target_goal_pledge_vote_requirement = serializers.SerializerMethodField()

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_token = validated_data.pop('stripe_token', None)
        customer_token = validated_data.pop('customer_token', None)
        ein = validated_data.pop('ein', None)
        ssn = validated_data.pop('ssn', None)
        active_prev = instance.active
        instance.active = validated_data.pop('activate', instance.active)
        instance.facebook = validated_data.get('facebook', instance.facebook)
        instance.linkedin = validated_data.get('linkedin', instance.linkedin)
        instance.youtube = validated_data.get('youtube', instance.youtube)
        instance.twitter = validated_data.get('twitter', instance.twitter)
        instance.website = validated_data.get('website', instance.website)
        instance.wallpaper_pic = validated_data.get('wallpaper_pic',
                                                    instance.wallpaper_pic)
        instance.profile_pic = validated_data.get('profile_pic',
                                                  instance.profile_pic)
        instance.biography = validated_data.get('biography',
                                                instance.biography)
        instance.epic = validated_data.get('epic', instance.epic)
        owner = Pleb.get(username=instance.owner_username)
        if customer_token is not None:
            customer = stripe.Customer.create(
                description="Customer for %s quest" % instance.object_uuid,
                card=customer_token,
                email=owner.email
            )
            instance.stripe_customer_id = customer['id']
            sub = customer.subscriptions.create(plan='quest_premium')
            instance.stripe_subscription_id = sub['id']
        if stripe_token is not None:
            if owner.stripe_account is None:
                stripe_res = stripe.Account.create(managed=True, country="US",
                                                   email=owner.email)
                owner.stripe_account = stripe_res['id']
                owner.save()
            owner_address = owner.get_address()
            instance.stripe_id = owner.stripe_account
            account = stripe.Account.retrieve(owner.stripe_account)
            account.external_accounts.create(external_account=stripe_token)
            account.legal_entity.additional_owners = []
            account.legal_entity.personal_id_number = ssn
            if ein:
                account.legal_entity.business_tax_id = ein
            account.legal_entity.first_name = owner.first_name
            account.legal_entity.last_name = owner.last_name
            account.legal_entity.type = "company"
            account.legal_entity.dob = dict(
                day=owner.date_of_birth.day,
                month=owner.date_of_birth.month,
                year=owner.date_of_birth.year
            )
            account.legal_entity.address.line1 = owner_address.street
            if owner_address.street_additional == "":
                owner_address.street_additional = None
            account.legal_entity.address.line2 = \
                owner_address.street_additional
            account.legal_entity.address.city = owner_address.city
            account.legal_entity.address.state = owner_address.state
            account.legal_entity.address.postal_code = \
                owner_address.postal_code
            account.legal_entity.address.country = "US"
            account.legal_entity.personal_address.line1 = owner_address.street
            if owner_address.street_additional == "":
                owner_address.street_additional = None
            account.legal_entity.personal_address.line2 = \
                owner_address.street_additional
            account.legal_entity.personal_address.city = owner_address.city
            account.legal_entity.personal_address.state = owner_address.state
            account.legal_entity.personal_address.postal_code = \
                owner_address.postal_code
            account.legal_entity.personal_address.country = \
                owner_address.country
            account.save()
            instance.last_four_soc = ssn[-4:]
        instance.save()
        instance.refresh()
        if not active_prev and instance.active:
            if not Campaign.get_active_round(instance.object_uuid):
                upcoming_round = Round.nodes.get(
                    object_uuid=Campaign.get_upcoming_round(
                        instance.object_uuid))
                instance.upcoming_round.disconnect(upcoming_round)
                instance.rounds.connect(upcoming_round)
                instance.active_round.connect(upcoming_round)
                upcoming_round.active = True
                upcoming_round.save()
                for goal in Round.get_goals(upcoming_round.object_uuid):
                    temp_goal = Goal.nodes.get(object_uuid=goal)
                    temp_goal.active = True
                    temp_goal.save()
                cache.set("%s_active_round" % instance.object_uuid,
                          upcoming_round.object_uuid)
                new_upcoming = Round().save()
                instance.upcoming_round.connect(new_upcoming)
                new_upcoming.campaign.connect(instance)
                cache.set("%s_upcoming_round" % instance.object_uuid,
                          new_upcoming.object_uuid)
        cache.set("%s_campaign" % instance.object_uuid, instance)
        return instance

    def get_url(self, obj):
        if obj.owner_username is not None and obj.owner_username != "":
            # We need a try catch here as there are some campaigns that have
            # username set but may not have a Pleb. This is only seen in tests
            # and has not been observed in production.
            username = obj.owner_username
        else:
            username = obj.object_uuid
        return reverse('quest_saga',
                       kwargs={"username": username},
                       request=self.context.get('request', None))

    def get_href(self, obj):
        return reverse('campaign-detail',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=self.context.get('request', None))

    def get_active_goals(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        active_goals = Campaign.get_active_goals(obj.object_uuid)
        if relation == 'hyperlink':
            return [reverse('goal-detail',
                            kwargs={'object_uuid': row}, request=request)
                    for row in active_goals]
        return active_goals

    def get_rounds(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        rounds = Campaign.get_rounds(obj.object_uuid)
        if relation == 'hyperlink':
            return [reverse('round-detail',
                            kwargs={'object_uuid': c_round},
                            request=request) for c_round in rounds]
        return rounds

    def get_active_round(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        active_round = Campaign.get_active_round(obj.object_uuid)
        if relation == 'hyperlink' and active_round is not None:
            return reverse('round-detail',
                           kwargs={'object_uuid': active_round},
                           request=request)
        return active_round

    def get_upcoming_round(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        upcoming_round = Campaign.get_upcoming_round(obj.object_uuid)
        if relation == 'hyperlink' and upcoming_round is not None:
            return reverse('round-detail',
                           kwargs={'object_uuid': upcoming_round},
                           request=request)
        return upcoming_round

    def get_updates(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        updates = Campaign.get_updates(obj.object_uuid)
        if relation == 'hyperlink':
            return [reverse('update-detail',
                            kwargs={'object_uuid': update},
                            request=request) for update in updates]
        return updates

    def get_position(self, obj):
        request, _, _, relations, _ = gather_request_data(self.context)
        position = Campaign.get_position(obj.object_uuid)
        if relations == 'hyperlink' and position is not None:
            return reverse('position-detail',
                           kwargs={'object_uuid': obj.object_uuid},
                           request=request)
        return position

    def get_public_official(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        public_official = PublicOfficialSerializer(obj.get_public_official(
            obj.object_uuid)).data
        if not public_official:
            return None
        return public_official

    def get_rendered_epic(self, obj):
        if obj.epic is not None:
            return markdown.markdown(obj.epic.replace('&gt;', '>'))
        else:
            return ""

    def get_completed_stripe(self, obj):
        if obj.stripe_id == "Not Set":
            return False
        return True

    def get_total_donation_amount(self, obj):
        return PoliticalCampaign.get_active_round_donation_total(
            obj.object_uuid)

    def get_total_pledge_vote_amount(self, obj):
        return PoliticalCampaign.get_vote_count(obj.object_uuid)

    def get_reputation(self, obj):
        if obj.owner_username is not None:
            # We need a try catch here as there are some campaigns that have
            # username set but may not have a Pleb. This is only seen in tests
            # and has not been observed in production.
            try:
                return Pleb.get(username=obj.owner_username).reputation
            except(DoesNotExist, Pleb.DoesNotExist):
                return None
        else:
            return None

    def get_target_goal_donation_requirement(self, obj):
        return Campaign.get_target_goal_donation_requirement(obj.object_uuid)

    def get_target_goal_pledge_vote_requirement(self, obj):
        return Campaign.get_target_goal_pledge_vote_requirement(
            obj.object_uuid)

    def get_is_editor(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        if request is None:
            return None
        return request.user.username in \
            PoliticalCampaign.get_editors(obj.object_uuid)

    def get_is_accountant(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        if request is None:
            return None
        return request.user.username in \
            PoliticalCampaign.get_accountants(obj.object_uuid)

    def get_completed_customer(self, obj):
        if obj.stripe_customer_id is None:
            return False
        return True


class PoliticalCampaignSerializer(CampaignSerializer):
    vote_type = serializers.SerializerMethodField()
    vote_count = serializers.SerializerMethodField()
    allow_vote = serializers.SerializerMethodField()
    constituents = serializers.SerializerMethodField()
    paid_account = serializers.SerializerMethodField()

    def create(self, validated_data):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        request = self.context.get('request', None)
        position = validated_data.pop('position', None)
        account_type = request.session.get('account_type', None)
        owner = Pleb.get(username=request.user.username)
        if account_type == 'paid':
            validated_data['application_fee'] = 0.021

        if owner.get_campaign():
            raise ValidationError(
                detail={"detail": "You may only have one quest!",
                        "developer_message": "",
                        "status_code": status.HTTP_400_BAD_REQUEST})
        official = owner.is_authorized_as()
        if official:
            validated_data['youtube'] = official.youtube
            validated_data['website'] = official.website
            validated_data['twitter'] = official.twitter
            validated_data['biography'] = official.bio
        try:
            formal_name = Position.get_full_name(
                position.object_uuid).get('full_name', None)
        except AttributeError:
            formal_name = None
        campaign = PoliticalCampaign(first_name=owner.first_name,
                                     last_name=owner.last_name,
                                     owner_username=owner.username,
                                     object_uuid=owner.username,
                                     profile_pic=owner.profile_pic,
                                     position_name=position.name,
                                     location_name=Position.get_location_name(
                                         position.object_uuid),
                                     position_formal_name=formal_name,
                                     **validated_data).save()
        if official:
            temp_camp = official.get_campaign()
            if temp_camp:
                official.campaign.disconnect(temp_camp)
                temp_camp.delete()
            official.campaign.connect(campaign)
            campaign.public_official.connect(official)
        campaign.owned_by.connect(owner)
        owner.campaign.connect(campaign)
        owner.campaign_editor.connect(campaign)
        owner.campaign_accountant.connect(campaign)
        campaign.position.connect(position)
        position.campaigns.connect(campaign)
        initial_round = Round().save()
        initial_round.campaign.connect(campaign)
        campaign.upcoming_round.connect(initial_round)
        campaign.editors.connect(owner)
        campaign.accountants.connect(owner)
        if owner.stripe_account is None:
            stripe_res = stripe.Account.create(managed=True, country="US",
                                               email=owner.email)
            owner.stripe_account = stripe_res['id']
            owner.save()
        account = stripe.Account.retrieve(owner.stripe_account)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        account.legal_entity.additional_owners = []
        account.tos_acceptance.ip = ip
        account.tos_acceptance.date = int(time.time())
        account.save()
        # Potential optimization in combining these utilizing a transaction
        # Added these to ensure that the user has intercom when they hit the
        # Quest page for the first time. The privilege still is fired through
        # the spawn_task as a backup and to ensure all connections are made
        # correctly
        epoch_date = datetime(1970, 1, 1, tzinfo=pytz.utc)
        query = 'MATCH (a:Pleb { username: "%s" }),' \
                '(b:SBAction {resource: "intercom"}) CREATE UNIQUE ' \
                '(a)-[r:CAN {active: true, gained_on: %f}]->(b) RETURN r' % (
                    owner.username, float((datetime.now(pytz.utc) -
                                           epoch_date).total_seconds()))
        db.cypher_query(query)
        query = 'MATCH (a:Pleb { username: "%s" }),' \
                '(b:Privilege {name: "quest"}) CREATE UNIQUE ' \
                '(a)-[r:HAS {active: true, gained_on: %f}]->(b) RETURN r' % (
                    owner.username, float((datetime.now(pytz.utc) -
                                           epoch_date).total_seconds()))
        db.cypher_query(query)
        cache.set("%s_campaign" % campaign.object_uuid, campaign)
        cache.delete(owner.username)
        cache.set("%s_privileges" % owner.username,
                  owner.get_privileges(cache_buster=True))
        cache.set("%s_actions" % owner.username,
                  owner.get_actions(cache_buster=True))
        spawn_task(task_func=check_privileges,
                   task_param={"username": owner.username})
        return campaign

    def get_vote_count(self, obj):
        return PoliticalCampaign.get_vote_count(obj.object_uuid)

    def get_constituents(self, obj):
        request, _, _, relation, expedite = gather_request_data(self.context)
        constituents = PoliticalCampaign.get_constituents(obj.object_uuid)
        if expedite == 'true':
            return []
        if relation == 'hyperlink':
            return [reverse('profile_page', kwargs={'pleb_username': row[0]},
                            request=request) for row in constituents]
        return constituents

    def get_vote_type(self, obj):
        request = self.context.get('request', None)
        if request is None:
            return None
        query = 'MATCH (c:PoliticalCampaign {object_uuid:"%s"})-' \
                '[r:RECEIVED_PLEDGED_VOTE]->(p:Pleb {username:"%s"}) ' \
                'RETURN r.active' % (obj.object_uuid, request.user.username)
        res, _ = db.cypher_query(query)
        return res.one

    def get_paid_account(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        if request is None:
            return None
        if request.user.username == obj.object_uuid:
            if obj.application_fee == 0.021:
                return True
            return False

    def get_allow_vote(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        try:
            pleb = Pleb.get(request.user.username)
        except (Pleb.DoesNotExist, DoesNotExist):
            return False
        address = pleb.get_address()
        address_encompassed_by = address.get_all_encompassed_by()
        encompassed_by = PoliticalCampaign.get_position_location(
            obj.object_uuid)
        if encompassed_by in address_encompassed_by:
            return True
        return False



class PoliticalVoteSerializer(serializers.Serializer):
    """
    The reason behind this serializer is to ensure that we can use the same
    functionality that voting on content uses, this just allows us to ensure
    that there are not multiple types of votes and that votes get toggled.

    The vote_type is set to a min and max 1 of to ensure that when
    someone votes it only modifies the active property of the vote
    relation. This is because we don't want people to be able to
    downvote a campaign, only allow them to pledge o vote or cancel
    their pledged vote.
    """
    vote_type = serializers.IntegerField(min_value=1, max_value=1)
    created = serializers.DateTimeField(read_only=True)
    active = serializers.BooleanField(read_only=True)


class EditorSerializer(serializers.Serializer):
    # profiles is expected to be a list of pleb usernames, not the entire pleb
    # object
    profiles = serializers.ListField(
        child=serializers.CharField(max_length=30)
    )

    def update(self, instance, validated_data):
        """
        The instance passed here much be a Campaign or any subclass of a
        Campaign
        :param instance:
        :param validated_data:
        :return:
        """
        current_editors = cache.get("%s_editors" % (instance.object_uuid), [])
        for profile in \
                list(set(validated_data['profiles']) - set(current_editors)):
            profile_pleb = Pleb.get(username=profile)
            instance.editors.connect(profile_pleb)
            profile_pleb.campaign_editor.connect(instance)
        cache.delete("%s_editors" % (instance.object_uuid))
        return instance

    def remove_profiles(self, instance):
        for profile in self.data['profiles']:
            profile_pleb = Pleb.get(username=profile)
            instance.editors.disconnect(profile_pleb)
            profile_pleb.campaign_editor.disconnect(instance)
        cache.delete("%s_editors" % (instance.object_uuid))
        return instance


class AccountantSerializer(serializers.Serializer):
    # profiles is expected to be a list of pleb usernames, not the entire pleb
    # object
    profiles = serializers.ListField(
        child=serializers.CharField(max_length=30)
    )

    def update(self, instance, validated_data):
        current_accountants = cache.get("%s_accountants" %
                                        (instance.object_uuid), [])
        for profile in \
                list(set(validated_data['profiles']) - set(
                     current_accountants)):
            profile_pleb = Pleb.get(username=profile)
            instance.accountants.connect(profile_pleb)
            profile_pleb.campaign_accountant.connect(instance)
        cache.delete("%s_accountants" % (instance.object_uuid))
        return instance

    def remove_profiles(self, instance):
        for profile in self.data['profiles']:
            profile_pleb = Pleb.get(username=profile)
            instance.accountants.disconnect(profile_pleb)
            profile_pleb.campaign_accountant.disconnect(instance)
        cache.delete("%s_accountants" % (instance.object_uuid))
        return instance


class PositionSerializer(SBSerializer):
    name = serializers.CharField()

    href = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    campaigns = serializers.SerializerMethodField()

    def get_href(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return reverse('position-detail',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=request)

    def get_campaigns(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        campaigns = Position.get_campaigns(obj.object_uuid)
        if relation == 'hyperlink':
            return [reverse('campaign-detail',
                            kwargs={'object_uuid': campaign},
                            request=request) for campaign in campaigns]
        return campaigns

    def get_location(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        location = Position.get_location(obj.object_uuid)
        if relation == 'hyperlink':
            return reverse('location-detail',
                           kwargs={'object_uuid': location},
                           request=request)
        return location

    def get_full_name(self, obj):
        return Position.get_full_name(obj.object_uuid)


class PositionManagerSerializer(SBSerializer):
    name = serializers.CharField()

    location_name = serializers.CharField(
        allow_blank=True)
    location_uuid = serializers.CharField(
        allow_blank=True)

    def create(self, validated_data):
        location = None
        location_name = validated_data.pop('location_name', '')
        location_id = validated_data.pop('location_uuid', '')
        try:
            location = Location.nodes.get(name=location_name)
        except(Location.DoesNotExist, DoesNotExist):
            pass
        if location is None:
            try:
                location = Location.nodes.get(object_uuid=location_id)
            except(Location.DoesNotExist, DoesNotExist):
                pass
        position = Position(**validated_data).save()
        if location is not None:
            location.positions.connect(position)
            position.location.connect(location)

        return position
