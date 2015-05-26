import pytz
from datetime import datetime
from logging import getLogger

from django.core.cache import cache

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import db, DoesNotExist

from api.serializers import SBSerializer
from api.utils import gather_request_data
from plebs.neo_models import Pleb
from sb_locations.neo_models import (Location)
from sb_goals.neo_models import Goal, Round

from .neo_models import (Campaign, PoliticalCampaign, Position)

logger = getLogger('loggly_logs')


class CampaignSerializer(SBSerializer):
    active = serializers.BooleanField(required=False)
    biography = serializers.CharField(required=True)
    facebook = serializers.CharField(required=False, allow_null=True)
    linkedin = serializers.CharField(required=False, allow_null=True)
    youtube = serializers.CharField(required=False, allow_null=True)
    twitter = serializers.CharField(required=False, allow_null=True)
    website = serializers.CharField(required=False, allow_null=True)
    wallpaper_pic = serializers.CharField(required=False, allow_null=True)
    profile_pic = serializers.CharField(required=False, allow_null=True)

    url = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()
    rounds = serializers.SerializerMethodField()
    updates = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()
    active_goals = serializers.SerializerMethodField()
    active_round = serializers.SerializerMethodField()
    upcoming_round = serializers.SerializerMethodField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
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
        instance.save()
        return instance

    def get_url(self, obj):
        return PoliticalCampaign.get_url(obj.object_uuid,
                                         request=self.context.get('request',
                                                                  None))

    def get_href(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return reverse('campaign-detail',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=request)

    def get_active_goals(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        active_goals = Campaign.get_active_goals(obj.object_uuid)
        if relation == 'hyperlink':
            return [reverse('goal-detail',
                            kwargs={'object_uuid':row}, request=request)
                    for row in active_goals]
        return active_goals

    def get_rounds(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        if relation == 'hyperlink':
            return reverse('round-list',
                           kwargs={'object_uuid': obj.object_uuid},
                           request=request)
        return Campaign.get_rounds(obj.object_uuid)

    def get_active_round(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        active_round = Campaign.get_active_round(obj.object_uuid)
        if relation == 'hyperlink':
            if active_round is None:
                return None
            return reverse('round-detail',
                           kwargs={'object_uuid': active_round},
                           request=request)
        return active_round

    def get_upcoming_round(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        upcoming_round = Campaign.get_upcoming_round(obj.object_uuid)
        if relation == 'hyperlink':
            if upcoming_round is None:
                return None
            return reverse('round-detail',
                           kwargs={'object_uuid': upcoming_round},
                           request=request)
        return upcoming_round

    def get_updates(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        relation_list = []
        updates = Campaign.get_updates(obj.object_uuid)
        if relation == 'hyperlink':
            for update in updates:
                relation_list.append(reverse('update-detail',
                                             kwargs={'object_uuid': update},
                                             request=request))
            return relation_list
        return updates

    def get_position(self, obj):
        request, _, _, relations, _ = gather_request_data(self.context)
        if relations == 'hyperlink':
            return reverse('campaign-position',
                           kwargs={'object_uuid': obj.object_uuid},
                           request=request)
        return Campaign.get_position(obj.object_uuid)


class PoliticalCampaignSerializer(CampaignSerializer):
    vote_count = serializers.SerializerMethodField()

    def create(self, validated_data):
        request, expand, _, _, _ = gather_request_data(self.context)
        owner = Pleb.get(request.user.username)
        validated_data['owner_username'] = owner.username
        campaign = PoliticalCampaign(**validated_data).save()
        campaign.owned_by.connect(owner)
        owner.campaign.connect(campaign)
        owner.campaign_editor.connect(campaign)
        owner.campaign_accountant.connect(campaign)
        initial_round = Round(start_date=datetime.now(pytz.utc)).save()
        initial_round.campaign.connect(campaign)
        campaign.upcoming_round.connect(initial_round)
        campaign.editors.connect(owner)
        campaign.accountants.connect(owner)
        cache.set(campaign.object_uuid, campaign)
        return campaign

    def get_vote_count(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return PoliticalCampaign.get_vote_count(obj.object_uuid)

    def get_constituents(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        constituents = PoliticalCampaign.get_constituents(obj.object_uuid)
        if relation == 'hyperlink':
            return [reverse('profile_page', kwargs={'pleb_username': row[0]},
                            request=request) for row in constituents]
        return constituents


class PoliticalVoteSerializer(serializers.Serializer):
    """
    The reason behind this serializer is to ensure that we can use the same
    functionality that voting on content uses, this just allows us to ensure
    that there are not multiple types of votes and that votes get toggled.
    """
    vote_type = serializers.IntegerField(min_value=1, max_value=1)


class EditorSerializer(serializers.Serializer):
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
        for profile in validated_data['profiles']:
            profile_pleb = Pleb.get(username=profile)
            instance.editors.connect(profile_pleb)
            profile_pleb.campaign_editor.connect(instance)
            cache.set(profile_pleb.username, profile_pleb)
        cache.delete("%s_editors" % (instance.object_uuid))
        return instance


class AccountantSerializer(serializers.Serializer):
    profiles = serializers.ListField(
        child=serializers.CharField(max_length=30)
    )

    def update(self, instance, validated_data):
        for profile in validated_data['profiles']:
            profile_pleb = Pleb.get(username=profile)
            instance.accountants.connect(profile_pleb)
            profile_pleb.campaign_accountant.connect(instance)
            cache.set(profile_pleb.username, profile_pleb)
        cache.delete("%s_accountants" % (instance.object_uuid))
        return instance


class PositionSerializer(serializers.Serializer):
    name = serializers.CharField()

    campaigns = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    def get_campaigns(self, obj):
        campaign_list = []
        request, expand, _, relation, _ = gather_request_data(self.context)
        campaigns = Position.get_campaigns(obj.object_uuid)
        if relation == 'hyperlink':
            for campaign in campaigns:
                campaign_list.append(reverse('campaign-detail',
                                             kwargs={'object_uuid':
                                                         campaign},
                                             request=request))
            return campaign_list
        return campaigns

    def get_location(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        location = Position.get_location(obj.object_uuid)
        if relation == 'hyperlink':
            return reverse('location-detail',
                           kwargs={'object_uuid': location},
                           request=request)
        return location
