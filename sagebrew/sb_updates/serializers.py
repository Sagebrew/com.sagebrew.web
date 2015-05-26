import bleach

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import db

from plebs.neo_models import Pleb
from sb_goals.neo_models import Goal
from api.utils import gather_request_data
from sb_campaigns.neo_models import Campaign
from sb_base.serializers import TitledContentSerializer

from .neo_models import Update



class UpdateSerializer(TitledContentSerializer):
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
        validated_data['owner_username'] = owner.username
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
        return Update.get_goals(obj.object_uuid)


    def get_campaign(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        campaign = Update.get_campaign(obj.object_uuid)
        if campaign is not None:
            if relation == 'hyperlink':
                return reverse('campaign-detail',
                               kwargs={'object_uuid': campaign},
                               request=request)
        return campaign

    def get_url(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return reverse('update-detail',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=request)
