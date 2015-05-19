from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel.exception import DoesNotExist
from neomodel import db

from sb_base.serializers import CampaignAttributeSerializer
from api.utils import spawn_task, gather_request_data
from plebs.neo_models import Address, Pleb, BetaUser
from plebs.tasks import create_pleb_task, pleb_user_update, determine_pleb_reps
from plebs.serializers import PlebSerializerNeo
from sb_campaigns.neo_models import PoliticalCampaign

from .neo_models import Goal, Round

class GoalSerializer(CampaignAttributeSerializer):
    initial = serializers.BooleanField(required=False)
    title = serializers.CharField(required=True)
    summary = serializers.CharField(required=True)
    description = serializers.CharField(required=False)
    pledged_vote_requirement = serializers.IntegerField(required=False)
    monetary_requirement = serializers.IntegerField(required=False)

    updates = serializers.SerializerMethodField()
    associated_round = serializers.SerializerMethodField()
    donations = serializers.SerializerMethodField()
    previous_goal = serializers.SerializerMethodField()
    next_goal = serializers.SerializerMethodField()

    def create(self, validated_data):
        campaign = validated_data.pop('campaign', None)
        campaign_round = validated_data.pop('round', None)
        goal = Goal(**validated_data).save()
        # TODO implement connecting to the next and prev goal logic
        if campaign is not None:
            campaign.goals.connect(goal)
            goal.campaign.connect(campaign)
        if campaign_round is not None:
            campaign_round.goals.connect(goal)
            goal.associated_round.connect(campaign_round)
        return goal


    def get_updates(self, obj):
        pass

    def get_round(self, obj):
        pass

    def get_donations(self, obj):
        pass

    def get_previous_goal(self, obj):
        pass

    def get_next_goal(self, obj):
        pass


class RoundSerializer(CampaignAttributeSerializer):
    active = serializers.BooleanField()
    start_date = serializers.DateTimeField(required=False)
    completed = serializers.DateTimeField(read_only=True)

    goals = serializers.SerializerMethodField()
    previous_round = serializers.SerializerMethodField()
    next_round = serializers.SerializerMethodField()

    def create(self, validated_data):
        campaign = validated_data.pop('campaign', None)
        previous_round = validated_data.pop('previous_round', None)
        next_round = validated_data.pop('next_round', None)
        campaign_round = Round(**validated_data).save()
        campaign = PoliticalCampaign.nodes.get(object_uuid=campaign)
        campaign.rounds.connect(campaign_round)
        campaign_round.campaign.connect(campaign)
        if previous_round is not None:
            prev_round = Round.nodes.get(object_uuid=previous_round)
            campaign_round.previous_round.connect(prev_round)
            prev_round.next_round.connect(campaign_round)
        if next_round is not None:
            next_round = Round.nodes.get(object_uuid=next_round)
            next_round.previous_round.connect(campaign_round)
            campaign_round.next_round.conect(next_round)
        return campaign_round

    def get_goals(self, obj):
        pass

    def get_previous_round(self, obj):
        pass

    def get_next_round(self, obj):
        pass
