from django.core.cache import cache

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import db

from api.utils import gather_request_data
from plebs.neo_models import Pleb
from sb_campaigns.neo_models import Campaign
from sb_goals.neo_models import Goal

from .neo_models import Donation


class DonationSerializer(serializers.Serializer):
    completed = serializers.BooleanField()
    amount = serializers.IntegerField()

    donated_for = serializers.SerializerMethodField()
    applied_to = serializers.SerializerMethodField()
    owned_by = serializers.SerializerMethodField()
    campaign = serializers.SerializerMethodField()

    def create(self, validated_data):
        request, _, _, _, _ = gather_request_data(self.context)
        donator = Pleb.get(request.user.username)
        donated_towards = request.data.pop('donated_towards', [])
        campaign_uuid = validated_data.pop('campaign', None)
        campaign = Campaign.nodes.get(object_uuid=campaign_uuid)
        donation = Donation(**validated_data).save()
        for goal in donated_towards:
            goal = Goal.nodes.get(object_uuid=goal)
            goal.donations.connect(donation)
            donation.donated_for.connect(goal)
        campaign.donations.connect(donation)
        donation.campaign.connect(campaign)
        donator.donations.connect(donation)
        donation.owned_by.connect(donator)
        cache.set(donator.username, donator)
        return donation

    def get_donated_for(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        query = 'MATCH (d:`Donation` {object_uuid: "%s"})-' \
                '[:DONATED_FOR]->(g:`Goal`) RETURN g.object_uuid' % (obj.object_uuid)
        res, col = db.cypher_query(query)
        if not res:
            return []
        return res[0]

    def get_applied_to(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        query = 'MATCH (d:`Donation` {object_uuid: "%s"})-' \
                '[:APPLIED_TO]->(g:`Goal`) RETURN g.object_uuid' % (obj.object_uuid)
        res, col = db.cypher_query(query)
        if not res:
            return []
        return res[0]

    def get_owned_by(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        query = 'MATCH (d:`Donation` {object_uuid: "%s"})-' \
                '[:DONATED_FROM]->(p:`Pleb`) RETURN p' % (obj.object_uuid)
        res, col = db.cypher_query(query)
        if not res:
            return []
        if relation == "hyperlink":
            return [reverse('profile_page',
                            kwargs={"pleb_username": res[0][0]},
                            request=request)]
        return res[0]

    def get_campaign(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        query = 'MATCH (d:`Donation` {object_uuid: "%s"})-' \
                '[:DONATED_FROM]->(p:`Pleb`) RETURN p' % (obj.object_uuid)
        res, col = db.cypher_query(query)
        if not res:
            return []
        if relation == "hyperlink":
            return [reverse('campaign-detail',
                            kwargs={"object_uuid": res[0][0]},
                            request=request)]
        return res[0]
