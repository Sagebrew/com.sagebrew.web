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
    description = serializers.CharField(required=False, allow_null=True)
    # We are requiring both a vote requirement and monetary requirement for
    # the first goal, the monetary requirement can be very small but it is
    # just easier for us with validation to allow them to make a monetary
    # requirement and vote requirement.
    pledged_vote_requirement = serializers.IntegerField(required=False,
                                                        allow_null=True)
    monetary_requirement = serializers.IntegerField(required=True,
                                                    allow_null=False)
    completed = serializers.BooleanField()
    completed_date = serializers.DateTimeField(allow_null=True)

    updates = serializers.SerializerMethodField()
    associated_round = serializers.SerializerMethodField()
    donations = serializers.SerializerMethodField()
    previous_goal = serializers.SerializerMethodField()
    next_goal = serializers.SerializerMethodField()

    def create(self, validated_data):
        campaign = validated_data.pop('campaign', None)
        campaign_round = Round.nodes.get(
            object_uuid=PoliticalCampaign.get_upcoming_round(
                campaign.object_uuid))
        next_goal = validated_data.pop('next_goal', None)
        previous_goal = validated_data.pop('previous_goal', None)
        goal = Goal(**validated_data).save()
        if next_goal is not None:
            next_goal.previous_goal.connect(goal)
            goal.next_goal.connect(next_goal)
        if previous_goal is not None:
            previous_goal.next_goal.connect(goal)
            goal.previous_goal.connect(previous_goal)
        if campaign is not None:
            campaign.goals.connect(goal)
            goal.campaign.connect(campaign)
        if campaign_round is not None:
            campaign_round.goals.connect(goal)
            goal.associated_round.connect(campaign_round)
        return goal


    def get_updates(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        updates = Goal.get_updates(obj.object_uuid)
        if relation == 'hyperlink':
            return [reverse('update-detail',
                            kwargs={'object_uuid': update}, request=request)
                    for update in updates]
        return updates

    def get_associated_round(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        associated_round = Goal.get_associated_round(obj.object_uuid)
        if relation == 'hyperlink' and associated_round is not None:
            return reverse('round-detail',
                           kwargs={'object_uuid': associated_round},
                           request=request)
        return associated_round

    def get_donations(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        return Goal.get_donations(obj.object_uuid)

    def get_previous_goal(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        prev_goal = Goal.get_previous_goal(obj.object_uuid)
        if relation == 'hyperlink' and prev_goal is not None:
            return reverse('goal-detail', kwargs={'object_uuid': prev_goal},
                           request=request)
        return prev_goal

    def get_next_goal(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        next_goal = Goal.get_next_goal(obj.object_uuid)
        if relation == 'hyperlink' and next_goal is not None:
            return reverse('goal-detail', kwargs={'object_uuid': next_goal},
                           request=request)
        return next_goal


class RoundSerializer(CampaignAttributeSerializer):
    active = serializers.BooleanField()
    start_date = serializers.DateTimeField(read_only=True)
    completed = serializers.DateTimeField(read_only=True)

    goals = serializers.SerializerMethodField()
    previous_round = serializers.SerializerMethodField()
    next_round = serializers.SerializerMethodField()

    def create(self, validated_data):
        campaign = validated_data.pop('campaign', None)
        previous_round = validated_data.pop('previous_round', None)
        next_round = validated_data.pop('next_round', None)
        campaign_round = Round(**validated_data).save()
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
        request, _, _, relation, _ = gather_request_data(self.context)
        goals = Round.get_goals(obj.object_uuid)
        if relation == 'hyperlink':
            return [reverse('goal-detail', kwargs={'object_uuid': row},
                            request=request) for row in goals]
        return goals

    def get_previous_round(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        prev_round = Round.get_previous_round(obj.object_uuid)
        if relation == 'hyperlink' and prev_round is not None:
            return reverse('round-detail', kwargs={'object_uuid': prev_round},
                           request=request)
        return prev_round

    def get_next_round(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        next_round = Round.get_next_round(obj.object_uuid)
        if relation == 'hyperlink' and next_round is not None:
            return reverse('round-detail', kwargs={'object_uuid': next_round},
                           request=request)
        return next_round
