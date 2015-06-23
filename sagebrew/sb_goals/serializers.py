import pytz
from datetime import datetime

from django.core.cache import cache

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import db

from sb_base.serializers import CampaignAttributeSerializer
from api.utils import gather_request_data
from sb_campaigns.neo_models import PoliticalCampaign

from .neo_models import Goal, Round


class GoalSerializer(CampaignAttributeSerializer):
    active = serializers.BooleanField(read_only=True)
    title = serializers.CharField(required=True)
    summary = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_null=True,
                                        allow_blank=True)
    target = serializers.BooleanField(required=False)
    # We are requiring both a vote requirement and monetary requirement for
    # the first goal, the monetary requirement can be very small but it is
    # just easier for us with validation to allow them to make a monetary
    # requirement and vote requirement.
    pledged_vote_requirement = serializers.IntegerField(required=False,
                                                        allow_null=True)
    monetary_requirement = serializers.IntegerField(required=True,
                                                    allow_null=False)
    completed = serializers.BooleanField(read_only=True)
    completed_date = serializers.DateTimeField(allow_null=True, read_only=True)
    total_required = serializers.IntegerField(required=False, allow_null=True)
    pledges_required = serializers.IntegerField(required=False,
                                                allow_null=True)

    updates = serializers.SerializerMethodField()
    associated_round = serializers.SerializerMethodField()
    donations = serializers.SerializerMethodField()
    previous_goal = serializers.SerializerMethodField()
    next_goal = serializers.SerializerMethodField()

    def create(self, validated_data):
        campaign = validated_data.pop('campaign', None)
        goal = Goal(**validated_data).save()
        campaign.goals.connect(goal)
        goal.campaign.connect(campaign)
        return goal

    def update(self, instance, validated_data):
        campaign = validated_data.pop('campaign', None)
        instance.title = validated_data.pop('title', instance.title)
        instance.summary = validated_data.pop('summary', instance.summary)
        instance.description = validated_data.pop('description',
                                                  instance.description)
        instance.pledged_vote_requirement = validated_data.pop(
            'pledged_vote_requirement', instance.pledged_vote_requirement)
        instance.monetary_requirement = validated_data.pop(
            'monetary_requirement', instance.monetary_requirement)
        instance.total_required = validated_data.pop('total_required',
                                                     instance.total_required)
        instance.pledges_required = validated_data.pop(
            'pledges_required', instance.pledges_required)
        campaign_round = Round.nodes.get(
            object_uuid=PoliticalCampaign.get_upcoming_round(campaign))
        campaign_round.goals.connect(instance)
        instance.associated_round.connect(campaign_round)
        prev_goal = validated_data.pop('prev_goal', None)
        if prev_goal is not None:
            query = 'MATCH (g:Goal {object_uuid:"%s"})-[:PREVIOUS]->' \
                    '(pg:Goal) RETURN pg' % (instance.object_uuid)
            res, _ = db.cypher_query(query)
            if res.one:
                temp_goal = Goal.inflate(res.one)
                instance.previous_goal.disconnect(temp_goal)
                temp_goal.next_goal.disconnect(instance)

            prev_goal = Goal.nodes.get(object_uuid=prev_goal)
            prev_goal.next_goal.connect(instance)
            instance.previous_goal.connect(prev_goal)
        else:
            instance.target = True
        instance.save()
        return instance

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
    active = serializers.BooleanField(read_only=True)
    queued = serializers.BooleanField()
    start_date = serializers.DateTimeField(read_only=True)
    completed = serializers.DateTimeField(read_only=True)

    goals = serializers.SerializerMethodField()
    previous_round = serializers.SerializerMethodField()
    next_round = serializers.SerializerMethodField()

    def update(self, instance, validated_data):
        instance.queued = validated_data.pop('queued', instance.queued)
        camp = PoliticalCampaign.nodes.get(
            object_uuid=Round.get_campaign(instance.object_uuid))
        if camp.active and not PoliticalCampaign.get_active_round(
                camp.object_uuid):
            instance.active = True
            instance.start_date = datetime.now(pytz.utc)
            camp.upcoming_round.disconnect(instance)
            camp.active_round.connect(instance)
            camp.round.connect(instance)
            cache.set("%s_active_round" % camp.object_uuid,
                      instance.object_uuid)
            new_upcoming = Round().save()
            camp.upcoming_round.connect(new_upcoming)
            new_upcoming.campaign.connect(camp)
            cache.set("%s_upcoming_round" % camp.object_uuid)
        instance.save()
        return instance

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
