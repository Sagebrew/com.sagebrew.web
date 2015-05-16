from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel.exception import DoesNotExist
from neomodel import db

from api.serializers import SBSerializer
from api.utils import spawn_task, gather_request_data
from plebs.neo_models import Address, Pleb, BetaUser
from plebs.tasks import create_pleb_task, pleb_user_update, determine_pleb_reps
from plebs.serializers import PlebSerializerNeo

from .neo_models import (Campaign, PoliticalCampaign, StateCampaign,
                         DistrictCampaign)


class CampaignSerializer(SBSerializer):
    stripe_id = serializers.CharField(required=False, allow_blank=True,
                                      allow_null=True)
    active = serializers.BooleanField(required=False)
    biography = serializers.CharField(required=True)
    facebook = serializers.CharField(required=False, allow_blank=True,
                                     allow_null=True)
    linkedin = serializers.CharField(required=False, allow_blank=True,
                                     allow_null=True)
    youtube = serializers.CharField(required=False, allow_blank=True,
                                    allow_null=True)
    twitter = serializers.CharField(required=False, allow_blank=True,
                                    allow_null=True)
    website = serializers.CharField(required=False, allow_blank=True,
                                    allow_null=True)

    wallpaper_pic = serializers.CharField(required=False, allow_blank=True,
                                    allow_null=True)
    profile_pic = serializers.CharField(required=False, allow_blank=True,
                                    allow_null=True)

    url = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()
    goals = serializers.SerializerMethodField()
    rounds = serializers.SerializerMethodField()
    updates = serializers.SerializerMethodField()
    editors = serializers.SerializerMethodField()
    accountants = serializers.SerializerMethodField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        instance.stripe_id = validated_data.get('stripe_id',
                                                instance.stripe_id)
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

    def get_type(self, obj):
        return "campaign"

    def get_url(self, obj):
        return obj.get_url(request=self.context.get('request', None))

    def get_href(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        return reverse('campaign-detail',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=request)

    def get_goals(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        pass

    def get_rounds(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        pass

    def get_updates(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        pass

    def get_editors(self, obj):
        return reverse('campaign-editors',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=self.context['request'])

    def get_accountants(self, obj):
        return reverse('campaign-accountants',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=self.context['request'])


class PoliticalCampaignSerializer(CampaignSerializer):
    votes = serializers.SerializerMethodField()
    vote_count = serializers.SerializerMethodField()

    def create(self, validated_data):
        request = self.context['request']
        owner = Pleb.get(request.user.username)
        editors = validated_data.pop('editors', [])
        accountants = validated_data.pop('accountants', [])
        campaign = PoliticalCampaign(**validated_data).save()
        campaign.owned_by.connect(owner)
        owner.campaign.connect(campaign)
        for editor in editors:
            editor_pleb = Pleb.get(editor)
            campaign.editors.connect(editor_pleb)
            editor_pleb.campaign_editor.connect(campaign)
        for accountant in accountants:
            accountant_pleb = Pleb.get(accountant)
            campaign.accountants.connect(accountant)
            accountant_pleb.campaign_accountant.connect(campaign)
        return campaign

    def get_votes(self, obj):
        pass

    def get_vote_count(self, obj):
        pass


class EditorAccountantSerializer(serializers.Serializer):
    users = serializers.ListField(
        child=serializers.CharField(max_length=30)
    )


class PledgeVoteSerializer(SBSerializer):
    pass
