import stripe

from django.conf import settings
from django.core.cache import cache
from django.template.loader import get_template
from django.template import Context

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import db

from api.utils import gather_request_data, spawn_task
from api.serializers import SBSerializer
from sb_base.serializers import IntercomMessageSerializer
from plebs.neo_models import Pleb
from plebs.serializers import PlebExportSerializer
from sb_privileges.tasks import check_privileges

from .neo_models import Donation


class DonationSerializer(SBSerializer):
    completed = serializers.BooleanField(read_only=True)
    amount = serializers.IntegerField(required=True, min_value=100)
    owner_username = serializers.CharField(read_only=True)
    payment_method = serializers.CharField(write_only=True, allow_null=True)

    mission_type = serializers.ChoiceField(read_only=True, choices=[
        ('position', "Public Office"), ('advocacy', "Advocacy"),
        ('question', "Question")])
    quest = serializers.SerializerMethodField()
    mission = serializers.SerializerMethodField()
    actual_amount = serializers.SerializerMethodField()

    def validate_amount(self, value):
        """
        Commenting out for time being until we can incorporate this into the
        frontend and also establish that 2700 is the actual max amount.
        Quests should be able to set this dynamically per mission and us
        display the max amount in the custom input field.

        from sb_missions.neo_models import Mission
        request = self.context.get('request', None)
        mission = Mission.get(self.context['view'].kwargs['object_uuid'])

        if mission.focus_on_type == "position":
            donation_amount = Pleb.get_mission_political_donations(
                request.user.username,
                self.context['view'].kwargs['object_uuid'])
            if donation_amount >= 270000:
                message = "You have already donated the max amount of " \
                          "$2700 to this " \
                          "mission for the year."
                raise serializers.ValidationError(message)
            if (donation_amount + value) > 270000:
                message = "You cannot donate $%s because you have already " \
                          "donated $%s and the max you can donate to this " \
                          "campaign is $%s." % (str(value)[:-2],
                                                str(donation_amount)[:-2],
                                                str(270000)[:-2])
                raise serializers.ValidationError(message)
        """
        if value < 0:
            message = "You cannot donate a negative amount of " \
                      "money to this mission"
            raise serializers.ValidationError(message)
        if value < 1:
            message = "Donations must be at least $1"
            raise serializers.ValidationError(message)
        if value > 1000000:
            # Limiting to less than $1,000,000.00 because stripe does not
            # allow charges over $999,999.99
            message = "Donations cannot be over $999,999.99"
            raise serializers.ValidationError(message)
        '''
        TODO @tyler is there a reason we weren't allowing donations with change?
        if not isinstance(value, int):
            raise serializers.ValidationError("Sorry donations cannot include "
                                              "change.")
        '''
        return value

    def create(self, validated_data):
        request, _, _, _, _ = gather_request_data(self.context)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = settings.STRIPE_API_VERSION
        mission = validated_data.pop('mission', None)
        quest = validated_data.pop('quest', None)
        donor = validated_data.pop('donor', None)
        payment_method = validated_data.pop('payment_method', None)
        validated_data['mission_type'] = mission.focus_on_type
        donation = Donation(**validated_data).save()

        donor.donations.connect(donation)
        donation.mission.connect(mission)

        quest_desc = quest.title \
            if quest.title else "%s %s" % (quest.first_name, quest.last_name)
        mission_desc = mission.get_mission_title()
        description = "Donation to %s's mission for %s" % (quest_desc,
                                                           mission_desc)
        payment_method = payment_method if payment_method is not None \
            else donor.stripe_default_card_id
        stripe_res = stripe.Charge.create(
            customer=donor.stripe_customer_id,
            amount=donation.amount,
            currency="usd",
            description=description,
            destination=quest.stripe_id,
            receipt_email=donor.email,
            source=payment_method,
            application_fee=int(
                (donation.amount * (quest.application_fee +
                                    settings.STRIPE_TRANSACTION_PERCENT)) + 30)
        )
        donation.stripe_charge_id = stripe_res['id']
        donation.completed = True
        donation.save()
        message_data = {
            'message_type': 'email',
            'subject': 'New Donation',
            'body': get_template('donations/email/new_donation.html').render(
                Context({
                    'first_name': quest.first_name,
                    'mission_title': mission_desc,
                    "amount": "%0.2f" % (donation.amount / 100.0),
                    "donor_first_name": donor.first_name,
                    "donor_last_name": donor.last_name,
                    "quest_donation_page": reverse(
                        'quest_stats',
                        kwargs={'username': quest.owner_username},
                        request=self.context.get('request'))
                })),
            'template': "personal",
            'from_user': {
                'type': "admin",
                'id': settings.INTERCOM_ADMIN_ID_DEVON
            },
            'to_user': {
                'type': "user",
                'user_id': quest.owner_username
            }
        }
        serializer = IntercomMessageSerializer(data=message_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cache.delete("%s_total_donated" % mission.object_uuid)
        cache.delete("%s_total_donated" % quest.object_uuid)
        cache.delete("%s_average_donation_amount" % mission.object_uuid)
        return donation

    def get_mission(self, obj):
        from sb_missions.neo_models import Mission
        from sb_missions.serializers import MissionSerializer
        request, expand, _, relation, _ = gather_request_data(self.context)
        mission = Donation.get_mission(obj.object_uuid)
        if mission is None:
            return None
        if expand == 'true':
            return MissionSerializer(Mission.get(
                object_uuid=mission)).data
        if relation == "hyperlink" and mission is not None:
            return reverse('mission-detail',
                           kwargs={"object_uuid": mission},
                           request=request)
        return mission

    def get_quest(self, obj):
        from sb_quests.neo_models import Quest
        from sb_quests.serializers import QuestSerializer
        request, expand, _, relation, _ = gather_request_data(self.context)
        query = 'MATCH (d:Donation {object_uuid: "%s"})-' \
                '[:CONTRIBUTED_TO]->' \
                '(mission:Mission)<-[:EMBARKS_ON]-(quest:Quest) ' \
                'RETURN quest' % obj.object_uuid
        res, _ = db.cypher_query(query)
        if res.one is None:
            return None
        quest = Quest.inflate(res.one)
        if expand == 'true':
            return QuestSerializer(quest).data
        if relation == "hyperlink":
            return reverse('quest-detail',
                           kwargs={"object_uuid": quest.object_uuid},
                           request=request)
        return quest.owner_username

    def get_actual_amount(self, obj):
        from sb_quests.neo_models import Quest
        query = 'MATCH (d:Donation {object_uuid: "%s"})-' \
                '[:CONTRIBUTED_TO]->' \
                '(mission:Mission)<-[:EMBARKS_ON]-(quest:Quest) ' \
                'RETURN quest' % obj.object_uuid
        res, _ = db.cypher_query(query)
        if res.one is None:
            return None
        quest = Quest.inflate(res.one)
        application_fee = obj.amount * (
            quest.application_fee +
            settings.STRIPE_TRANSACTION_PERCENT) + 30
        return '{:,.2f}'.format(float(obj.amount - application_fee) / 100)


class DonationExportSerializer(serializers.Serializer):
    completed = serializers.BooleanField(read_only=True)
    mission_type = serializers.ChoiceField(read_only=True, choices=[
        ('position', "Public Office"), ('advocacy', "Advocacy"),
        ('question', "Question")])
    amount = serializers.SerializerMethodField()
    owned_by = serializers.SerializerMethodField()

    def get_owned_by(self, obj):
        serialized = PlebExportSerializer(Pleb.get(obj.owner_username)).data
        if obj.mission_type != "position":
            serialized.pop('occupation_name', None)
            serialized.pop('employer_name', None)
        return serialized

    def get_amount(self, obj):
        return obj.amount


class SBDonationSerializer(DonationSerializer):

    def validate_amount(self, value):
        return value

    def create(self, validated_data):
        request, _, _, _, _ = gather_request_data(self.context)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = settings.STRIPE_API_VERSION
        donor = Pleb.get(request.user.username)
        token = validated_data.pop('token', None)
        # TODO add payment_method selection support to direct donations
        # this pop is just to allow the donation to save using **validated_data
        validated_data.pop('payment_method', None)
        donation = Donation(owner_username=donor.username,
                            **validated_data).save()
        if not donor.stripe_customer_id:
            customer = stripe.Customer.create(
                description="Customer for %s" % donor.username,
                card=token,
                email=donor.email)
            donor.stripe_customer_id = customer['id']
            donor.save()
            cache.delete(donor.username)
            donor.refresh()
        donor.donations.connect(donation)
        donation.owned_by.connect(donor)
        charge = stripe.Charge.create(
            amount=donation.amount,
            currency="usd",
            customer=donor.stripe_customer_id,
            receipt_email=donor.email,
            description="Donation to Sagebrew from %s" % donor.username
        )
        donation.stripe_charge_id = charge['id']
        donation.save()
        spawn_task(task_func=check_privileges,
                   task_param={"username": donor.username})
        return donation
