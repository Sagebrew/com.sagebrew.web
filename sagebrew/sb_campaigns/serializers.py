import stripe
import markdown
from logging import getLogger

from django.core.cache import cache

from rest_framework import serializers, status
from rest_framework.reverse import reverse
from rest_framework.exceptions import ValidationError

from api.serializers import SBSerializer
from api.utils import gather_request_data
from plebs.neo_models import Pleb
from sb_goals.neo_models import Round
from sb_public_official.serializers import PublicOfficialSerializer

from .neo_models import (Campaign, PoliticalCampaign, Position)

logger = getLogger('loggly_logs')


class CampaignSerializer(SBSerializer):
    active = serializers.BooleanField(required=False, read_only=True)
    biography = serializers.CharField(required=False, max_length=150)
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

    url = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()
    rounds = serializers.SerializerMethodField()
    updates = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()
    active_goals = serializers.SerializerMethodField()
    active_round = serializers.SerializerMethodField()
    rendered_epic = serializers.SerializerMethodField()
    upcoming_round = serializers.SerializerMethodField()
    public_official = serializers.SerializerMethodField()
    completed_stripe = serializers.SerializerMethodField()
    total_donation_amount = serializers.SerializerMethodField()
    total_pledge_vote_amount = serializers.SerializerMethodField()

    def create(self, validated_data):
        request = self.context.get('request', None)
        owner = Pleb.get(request.user.username)
        validated_data['owner_username'] = owner.username
        campaign = Campaign(**validated_data).save()
        campaign.owned_by.connect(owner)
        owner.campaign.connect(campaign)
        owner.campaign_editor.connect(campaign)
        owner.campaign_accountant.connect(campaign)
        initial_round = Round().save()
        initial_round.campaign.connect(campaign)
        campaign.upcoming_round.connect(initial_round)
        campaign.editors.connect(owner)
        campaign.accountants.connect(owner)
        cache.set(campaign.object_uuid, campaign)
        return campaign

    def update(self, instance, validated_data):
        from logging import getLogger
        logger = getLogger('loggly_logs')
        stripe.api_key = "sk_test_4VQN8LrYMe8xbLH5v9kLMoKt"
        stripe_token = validated_data.pop('stripe_token', None)
        instance.active = validated_data.get('active', instance.active)
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
        logger.info(stripe_token)
        if stripe_token is not None:
            owner = Pleb.nodes.get(username=instance.owner_username)
            if owner.stripe_account is None:
                stripe_res = stripe.Account.create(managed=True, country="US",
                                                   email=owner.email)
                owner.stripe_account = stripe_res['id']
                owner.save()
            logger.info(owner.stripe_account)
            account = stripe.Account.retrieve(owner.stripe_account)
            bank_res = account.external_accounts.create(
                external_account=stripe_token)
            logger.info(account)
            logger.info(bank_res)
            instance.stripe_id = bank_res['id']
        instance.save()
        cache.set("%s_campaign" % instance.object_uuid, instance)
        return instance

    def get_url(self, obj):
        return reverse('quest_saga',
                       kwargs={"username": obj.object_uuid},
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


class PoliticalCampaignSerializer(CampaignSerializer):
    vote_count = serializers.SerializerMethodField()
    constituents = serializers.SerializerMethodField()

    def create(self, validated_data):
        request = self.context.get('request', None)
        position = validated_data.pop('position', None)
        owner = Pleb.get(username=request.user.username)
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
        campaign = PoliticalCampaign(first_name=owner.first_name,
                                     last_name=owner.last_name,
                                     owner_username=owner.username,
                                     object_uuid=owner.username,
                                     profile_pic=owner.profile_pic,
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
        cache.set("%s_campaign" % campaign.object_uuid, campaign)
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
            instance.accountants.disconnect(profile_pleb)
            profile_pleb.campaign_accountant.disconnect(instance)
        cache.delete("%s_accountants" % (instance.object_uuid))
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

    def remove_profiles(self, instance,):
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
