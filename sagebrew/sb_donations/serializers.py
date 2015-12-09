import stripe

from django.conf import settings
from django.template.loader import render_to_string
from django.core.cache import cache

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import db

from api.utils import gather_request_data, spawn_task
from api.serializers import SBSerializer
from plebs.neo_models import Pleb
from plebs.serializers import PlebExportSerializer
from sb_quests.neo_models import Campaign
from sb_quests.tasks import release_single_donation_task
from sb_goals.neo_models import Round
from sb_goals.tasks import check_goal_completion_task
from plebs.tasks import send_email_task
from sb_privileges.tasks import check_privileges

from .neo_models import Donation


class DonationSerializer(SBSerializer):
    completed = serializers.BooleanField(read_only=True)
    amount = serializers.IntegerField(required=True)
    owner_username = serializers.CharField(read_only=True)

    donated_for = serializers.SerializerMethodField()
    applied_to = serializers.SerializerMethodField()
    owned_by = serializers.SerializerMethodField()
    quest = serializers.SerializerMethodField()

    def validate_amount(self, value):
        request = self.context.get('request', None)
        donation_amount = Pleb.get_campaign_donations(
            request.user.username, self.context['view'].kwargs['object_uuid'])
        if value < 0:
            message = "You cannot donate a negative amount of " \
                      "money to this campaign."
            raise serializers.ValidationError(message)
        if donation_amount >= 270000:
            message = "You have already donated the max amount to this " \
                      "campaign."
            raise serializers.ValidationError(message)
        if (donation_amount + value) > 270000:
            message = "You cannot donate $%s because you have already " \
                      "donated $%s and the max you can donate to this " \
                      "campaign is $%s." % (str(value)[:-2],
                                            str(donation_amount)[:-2],
                                            str(270000)[:-2])
            raise serializers.ValidationError(message)
        if not isinstance(value, int):
            raise serializers.ValidationError("Sorry donations cannot include "
                                              "change.")
        return value

    def create(self, validated_data):
        request, _, _, _, _ = gather_request_data(self.context)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        donor = Pleb.get(request.user.username)
        token = validated_data.pop('token', None)
        validated_data['owner_username'] = donor.username
        campaign = validated_data.pop('campaign', None)
        donation = Donation(**validated_data).save()
        if not donor.stripe_customer_id:
            customer = stripe.Customer.create(
                description="Customer for %s" % donor.email,
                card=token,
                email=donor.email)
            donor.stripe_customer_id = customer['id']
            donor.save()
            cache.delete(donor.username)
            donor.refresh()
        current_round = Round.nodes.get(
            object_uuid=Campaign.get_active_round(campaign.object_uuid))
        current_round.donations.connect(donation)
        donation.associated_round.connect(current_round)
        # this is commented out because we cannot currently foresee any
        # use cases for it but we may need it in the future.
        """
        donated_toward = Goal.inflate(
            Campaign.get_current_target_goal(campaign.object_uuid))
        cache.set("%s_target_goal" % (campaign.object_uuid), donated_toward)
        donated_toward.donations.connect(donation)
        donation.donated_for.connect(donated_toward)
        """
        # This query manages the relationships between the new donation and
        # the goals in which it will be applied to
        # It gets the current active round of a campaign and gets the sum of
        # the donations on that round, this includes the new donation so the
        # donation has to be connected to the current round before this query
        # is ran. It totals the amount of donations given to this round then
        # gets all the goals whose total_required is less than or equal to the
        # total amount of donations and those who have not been completed. It
        # then gets the goal with the highest total_required and gets the next
        # goal from that to see if the new donation needs to be applied to the
        # next goal as well, this occurs when a donation amount will be
        # applied to partially complete a goal. It then creates the
        # connections between the goals which the donation will be applied to.
        query = 'MATCH (r:Round {object_uuid:"%s"}) WITH r OPTIONAL MATCH ' \
                '(r)-[:HAS_DONATIONS]->(d:Donation) WITH r, d MATCH ' \
                '(cd:Donation {object_uuid:"%s"}) WITH r, SUM(d.amount) ' \
                'as total_amount, cd, d MATCH (r)-[:STRIVING_FOR]->' \
                '(goals:Goal) WHERE goals.completed=false AND ' \
                'goals.total_required-total_amount<=0 FOREACH ' \
                '(goal IN [goals]|MERGE (cd)-[:APPLIED_TO]->(goal) ' \
                'MERGE (goal)-[:RECEIVED]->(cd))' \
                % (Campaign.get_active_round(campaign.object_uuid),
                   donation.object_uuid)
        db.cypher_query(query)
        campaign.donations.connect(donation)
        donation.campaign.connect(campaign)
        donor.donations.connect(donation)
        donation.owned_by.connect(donor)
        cache.delete("%s_total_donated" % campaign.object_uuid)
        if campaign.get_total_donated(campaign.object_uuid) \
                < settings.FREE_RELEASE_LIMIT:
            spawn_task(task_func=release_single_donation_task,
                       task_param={"donation_uuid": donation.object_uuid})
            return donation
        email_data = {
            "source": "support@sagebrew.com",
            "to": donor.email,
            "subject": "Thank you for your Quest Donation!",
            "html_content": render_to_string(
                "email_templates/email_quest_donation_pledge.html")
        }

        spawn_task(task_func=send_email_task,
                   task_param=email_data)
        spawn_task(task_func=check_goal_completion_task,
                   task_param={"round_uuid": current_round.object_uuid})
        spawn_task(task_func=check_privileges,
                   task_param={"username": donor.username})
        return donation

    def get_donated_for(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        donated_for = Donation.get_donated_for(obj.object_uuid)
        if relation == 'hyperlink' and donated_for is not None:
            return reverse('goal-detail', kwargs={'object_uuid': donated_for},
                           request=request)
        return donated_for

    def get_applied_to(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        applied_to = Donation.get_applied_to(obj.object_uuid)
        if relation == 'hyperlink' and applied_to is not None:
            return [reverse('goal-detail', kwargs={'object_uuid': goal},
                            request=request) for goal in applied_to]
        return applied_to

    def get_owned_by(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        if relation == "hyperlink":
            return reverse('profile_page',
                           kwargs={"pleb_username": obj.owner_username},
                           request=request)
        return obj.owner_username

    def get_mission(self, obj):
        from sb_missions.neo_models import Mission
        from sb_missions.serializers import MissionSerializer
        request, expand, _, relation, _ = gather_request_data(self.context)
        mission = Donation.get_mission(obj.object_uuid)
        if expand == 'true':
            return MissionSerializer(Mission.get(
                object_uuid=mission.object_uuid)).data
        if relation == "hyperlink" and mission is not None:
            return reverse('mission-detail',
                           kwargs={"object_uuid": mission},
                           request=request)
        return mission.object_uuid


class DonationExportSerializer(serializers.Serializer):
    completed = serializers.BooleanField(read_only=True)

    amount = serializers.SerializerMethodField()
    owned_by = serializers.SerializerMethodField()

    def get_owned_by(self, obj):
        return PlebExportSerializer(Pleb.get(obj.owner_username)).data

    def get_amount(self, obj):
        return float(obj.amount) / 100.0


class SBDonationSerializer(DonationSerializer):
    def validate_amount(self, value):
        return value

    def create(self, validated_data):
        request, _, _, _, _ = gather_request_data(self.context)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        donor = Pleb.get(request.user.username)
        token = validated_data.pop('token', None)
        donation = Donation(owner_username=donor.username,
                            **validated_data).save()
        if not donor.stripe_customer_id:
            customer = stripe.Customer.create(
                description="Customer for %s" % donor.email,
                card=token,
                email=donor.email)
            donor.stripe_customer_id = customer['id']
            donor.save()
            cache.delete(donor.username)
            donor.refresh()
        donor.donations.connect(donation)
        donation.owned_by.connect(donor)
        stripe.Charge.create(
            amount=donation.amount,
            currency="usd",
            customer=donor.stripe_customer_id,
            description="Donation to Sagebrew from %s" % donor.username
        )
        user_data = {
            "source": "support@sagebrew.com",
            "to": donor.email,
            "subject": "Thank you for your Donation!",
            "html_content": render_to_string(
                "email_templates/email_sagebrew_donation_thanks.html")
        }
        spawn_task(send_email_task, user_data)
        spawn_task(task_func=check_privileges,
                   task_param={"username": donor.username})
        return donation
