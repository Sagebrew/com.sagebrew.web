from json import loads
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

from .neo_models import (PoliticalCampaign, Position)

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
    goals = serializers.SerializerMethodField()
    rounds = serializers.SerializerMethodField()
    updates = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()
    active_goals = serializers.SerializerMethodField()
    active_round = serializers.SerializerMethodField()

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
        return obj.get_url(request=self.context.get('request', None))

    def get_href(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return reverse('campaign-detail',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=request)

    def get_goals(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return reverse('goal-list', kwargs={'object_uuid': obj.object_uuid},
                       request=request)

    def get_active_goals(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        query = "MATCH (r:`Campaign` {object_uuid:'%s'})-[:HAS_ROUND]->" \
                "(r:`Round`)-[:STRIVING_FOR]->(g:`Goal`) WHERE " \
                "r.active=true RETURN g.object_uuid ORDER BY g.created" % (obj.object_uuid)
        res, col = db.cypher_query(query)
        if not res:
            return []
        return res[0]

    def get_rounds(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return reverse('round-list',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=request)

    def get_active_round(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        query = "MATCH (r:`Campaign` {object_uuid:'%s'})-[:HAS_ROUND]->" \
                "(r:`Round`) WHERE r.active=true RETURN r.object_uuid" % \
                (obj.object_uuid)
        res, col = db.cypher_query(query)
        if not res:
            return []
        return res[0]

    def get_updates(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        relation_list = []
        query = 'MATCH (c:`Campaign` {object_uuid:"%s"})-[:HAS_UPDATE]-' \
                '(u:`Update`) WHERE u.to_be_deleted=false ' \
                'RETURN u.object_uuid' % (obj.object_uuid)
        res, col = db.cypher_query(query)
        if relation == 'hyperlink':
            for update in [row[0] for row in res]:
                relation_list.append(reverse('update-detail',
                                             kwargs={'object_uuid':
                                                         obj.object_uuid,
                                                     'updated_uuid': update},
                                             request=request))
        if not res:
            return []
        return res[0]

    def get_position(self, obj):
        request, _, _, relations, _ = gather_request_data(self.context)
        if relations == 'hyperlink':
            return reverse('campaign-position',
                           kwargs={'object_uuid': obj.object_uuid},
                           request=request)
        query = "MATCH (r:`Campaign` {object_uuid:'%s'})-[:RUNNING_FOR]->" \
                "(p:`Position`) RETURN p.object_uuid" % (obj.object_uuid)
        res, col = db.cypher_query(query)
        if not res:
            return []
        return res[0]


class PoliticalCampaignSerializer(CampaignSerializer):
    votes = serializers.SerializerMethodField()
    vote_count = serializers.SerializerMethodField()

    def create(self, validated_data):
        request, expand, _, _, _ = gather_request_data(self.context)
        owner = Pleb.get(request.user.username)
        campaign = PoliticalCampaign(**validated_data).save()
        campaign.owned_by.connect(owner)
        owner.campaign.connect(campaign)
        owner.campaign_editor.connect(campaign)
        owner.campaign_accountant.connect(campaign)
        campaign.editors.connect(owner)
        campaign.accountants.connect(owner)
        cache.set(campaign.object_uuid, campaign)
        return campaign

    def get_votes(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        pass

    def get_vote_count(self, obj):
        pass


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
        query = 'MATCH (p:`Position` {object_uuid: "%s"})-[:CAMPAIGNS]-' \
                '(c:`PoliticalCampaign`) RETURN c.object_uuid' % (obj.object_uuid)
        res, col = db.cypher_query(query)
        if relation == 'hyperlink':
            for campaign in [row[0] for row in res]:
                campaign_list.append(reverse('campaign-detail',
                                             kwargs={'object_uuid':
                                                         campaign},
                                             request=request))
            return campaign_list
        return [row[0] for row in res]

    def get_location(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        query = 'MATCH (p:`Position` {object_uuid: "%s"})-' \
                '[:AVAILABLE_WITHIN]-(c:`Location`) ' \
                'RETURN c.object_uuid' % (obj.object_uuid)
        res, col = db.cypher_query(query)
        if relation == 'hyperlink':
            return reverse('location-detail',
                           kwargs={'object_uuid': res[0][0]},
                           request=request)
        return [row[0] for row in res]
