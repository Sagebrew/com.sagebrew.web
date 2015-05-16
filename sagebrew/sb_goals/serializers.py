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

from .neo_models import Goal

class GoalSerializer(CampaignAttributeSerializer):
    initial = serializers.BooleanField(required=False)
    title = serializers.CharField(required=True)
    summary = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    pledged_vote_requirement = serializers.IntegerField(required=True)
    monetary_requirement = serializers.IntegerField(required=True)

    updates = serializers.SerializerMethodField()
    round = serializers.SerializerMethodField()
    donations = serializers.SerializerMethodField()
    previous_goal = serializers.SerializerMethodField()
    next_goal = serializers.SerializerMethodField()

    def create(self, validated_data):
        campaign = validated_data.pop('campaign', None)
        campaign_round = validated_data.pop('round', None)
        goal = Goal(**validated_data).save()
        # TODO implement connecting to the next and prev goal logic
        campaign.goals.connect(goal)
        campaign_round.goals.connect(goal)
        goal.campaign.connect(campaign)
        goal.round.connect(campaign_round)
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
    start_date = serializers.DateTimeField(required=False)
    completed = serializers.DateTimeField(required=False)

    goals = serializers.SerializerMethodField()
    previous_round = serializers.SerializerMethodField()
    next_round = serializers.SerializerMethodField()

    def get_goals(self, obj):
        pass

    def get_previous_round(self, obj):
        pass

    def get_next_round(self, obj):
        pass
