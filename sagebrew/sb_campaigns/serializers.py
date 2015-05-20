from json import loads
from logging import getLogger

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import db, DoesNotExist

from api.serializers import SBSerializer
from api.utils import gather_request_data
from plebs.neo_models import Pleb
from sb_locations.neo_models import (Location)

from .neo_models import (PoliticalCampaign, Position)

logger = getLogger('loggly_logs')


class CampaignSerializer(SBSerializer):
    stripe_id = serializers.CharField(write_only=True, allow_blank=True,
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
    rounds = serializers.SerializerMethodField()
    updates = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()
    active_goals = serializers.SerializerMethodField()

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

    def get_url(self, obj):
        return obj.get_url(request=self.context.get('request', None))

    def get_href(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return reverse('campaign-detail',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=request)

    def get_active_goals(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        return reverse('goals-list',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=request)

    def get_rounds(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return reverse('rounds-list',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=request)

    def get_updates(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        pass

    def get_position(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        return reverse('campaign-position',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=request)


class PoliticalCampaignSerializer(CampaignSerializer):
    votes = serializers.SerializerMethodField()
    vote_count = serializers.SerializerMethodField()

    def create(self, validated_data):
        request, expand, _, _, _ = gather_request_data(self.context)
        owner = Pleb.get(request.user.username)
        position = validated_data.pop('position', None)
        position = Position.nodes.get(object_uuid=position)
        campaign = PoliticalCampaign(**validated_data).save()
        campaign.position.connect(position)
        position.campaigns.connect(campaign)
        campaign.owned_by.connect(owner)
        owner.campaign.connect(campaign)
        owner.campaign_editor.connect(campaign)
        owner.campaign_accountant.connect(campaign)
        campaign.editors.connect(owner)
        campaign.accountants.connect(owner)
        return campaign

    def get_votes(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        pass

    def get_vote_count(self, obj):
        pass


class EditorAccountantSerializer(serializers.Serializer):
    profiles = serializers.ListField(
        child=serializers.CharField(max_length=30)
    )

    def create(self, validated_data):
        profile_type = validated_data.pop('profile_type', None)
        modification_type = validated_data.pop('modification_type', None)
        single_object = validated_data.pop('single_object', None)
        logger.info(validated_data)
        for profile in validated_data['profiles']:
            profile_pleb = Pleb.get(username=profile)
            if profile_type == "editor":
                if modification_type == "delete":
                    single_object.editors.disconnect(profile_pleb)
                    profile_pleb.campaign_editor.disconnect(single_object)
                else:
                    single_object.editors.connect(profile_pleb)
                    profile_pleb.campaign_editor.connect(single_object)
            elif profile_type == "accountant":
                if modification_type == "delete":
                    single_object.accountants.disconnect(profile_pleb)
                    profile_pleb.campaign_accountant.disconnect(single_object)
                else:
                    single_object.accountants.connect(profile_pleb)
                    profile_pleb.campaign_accountant.connect(single_object)
        return single_object



class PositionSerializer(serializers.Serializer):
    name = serializers.CharField()

    campaigns = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    def get_campaigns(self, obj):
        campaign_list = []
        request, expand, _, _, _ = gather_request_data(self.context)
        query = 'MATCH (p:`Position` {object_uuid: "%s"})--' \
                '(c:`PoliticalCampaign`) RETURN c' % (obj.object_uuid)
        res, col = db.cypher_query(query)
        for campaign in [PoliticalCampaign.inflate(row[0]) for row in res]:
            if expand == 'true':
                campaign_list.append(
                    PoliticalCampaignSerializer(campaign,
                                                context=
                                                {'request': request}).data)
            campaign_list.append(
                reverse('campaign-detail',
                        kwargs={'object_uuid': campaign.object_uuid},
                        request=request))
        return campaign_list

    def get_location(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        query = 'MATCH (p:`Position` {object_uuid: "%s"})--(c:`Location`) ' \
                'RETURN c' % (obj.object_uuid)
        res, col = db.cypher_query(query)
        node = [Location.inflate(row[0]) for row in res][0]
        return reverse('location-detail',
                       kwargs={'object_uuid': node.object_uuid},
                       request=request)
