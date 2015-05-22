import bleach

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import db

from plebs.neo_models import Pleb
from sb_goals.neo_models import Goal
from api.utils import gather_request_data
from sb_campaigns.neo_models import Campaign
from sb_base.serializers import MarkdownContentSerializer

from .neo_models import Update



class UpdateSerializer(MarkdownContentSerializer):
    title = serializers.CharField()

    goals = serializers.SerializerMethodField()
    campaign = serializers.SerializerMethodField()

    def create(self, validated_data):
        request, _, _, _, _ = gather_request_data(self.context)
        goals = request.data.pop('goals', [])
        campaign = request.data.pop('campaign', None)
        validated_data['content'] = bleach.clean(validated_data.get(
            'content', ""))
        owner = Pleb.get(request.user.username)
        campaign = Campaign.get(campaign)
        update = Update(**validated_data).save()
        update.campaign.connect(campaign)
        campaign.updates.connect(update)
        update.owned_by.connect(owner)
        for goal_id in goals:
            goal = Goal.nodes.get(object_uuid=goal_id)
            update.goals.connect(goal)
            goal.updates.connect(goal)
        return update

    def get_goals(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        query = 'MATCH (u:`Update` {object_uuid:"%s"})-[:FOR_A]-(g:`Goal`) ' \
                'RETURN g.object_uuid' % (obj.object_uuid)
        res, col = db.cypher_query(query)
        return [row[0] for row in res]


    def get_campaign(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        query = 'MATCH (u:`Update` {object_uuid:"%s"})-[:ON_THE]-' \
                '(c:`Campaign`) RETURN c.object_uuid' % (obj.object_uuid)
        res, col = db.cypher_query(query)
        if relation == 'hyperlink':
            return reverse('campaign-detail',
                           kwargs={'object_uuid': res[0][0]}, request=request)
        return [row[0] for row in res]
