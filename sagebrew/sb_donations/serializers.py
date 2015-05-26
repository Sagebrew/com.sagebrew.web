from django.core.cache import cache

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import db

from api.utils import gather_request_data
from plebs.neo_models import Pleb
from sb_campaigns.neo_models import Campaign
from sb_goals.neo_models import Goal

from .neo_models import Donation


class DonationValue:
    def __init__(self):
        self.limit = 270000

    def __call__(self, value):
        if value > self.limit:
            message = "You cannot donate over $%s to this campaign." % \
                      (str(self.limit)[:-2])
            raise serializers.ValidationError(message)


class DonationSerializer(serializers.Serializer):
    completed = serializers.BooleanField()
    amount = serializers.IntegerField(validators=[DonationValue(),])
    owner_username = serializers.CharField(read_only=True)

    donated_for = serializers.SerializerMethodField()
    applied_to = serializers.SerializerMethodField()
    owned_by = serializers.SerializerMethodField()
    campaign = serializers.SerializerMethodField()

    def validate_amount(self, value):
        request, _, _, _, _ = gather_request_data(self.context)
        donation_amount = Pleb.get_campaign_donations(
            request.user.username, self.context['view'].kwargs['object_uuid'])
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
        return value

    def create(self, validated_data):
        request, _, _, _, _ = gather_request_data(self.context)
        donor = Pleb.get(request.user.username)
        validated_data['owner_username'] = donor.username
        donated_towards = request.data.pop('donated_towards', [])
        campaign = validated_data.pop('campaign', None)
        donation = Donation(**validated_data).save()
        for goal in donated_towards:
            goal = Goal.nodes.get(object_uuid=goal)
            goal.donations.connect(donation)
            donation.donated_for.connect(goal)
        campaign.donations.connect(donation)
        donation.campaign.connect(campaign)
        donation.owned_by.connect(donor)
        donor.donations.connect(donation)
        donor.refresh()
        cache.set(donor.username, donor)
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
            return [reverse('profile_page',
                            kwargs={"pleb_username": obj.owner_username},
                            request=request)]
        return obj.owner_username

    def get_campaign(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        campaign = Donation.get_campaign(obj.object_uuid)
        if relation == "hyperlink":
            return reverse('campaign-detail',
                            kwargs={"object_uuid": campaign},
                            request=request)
        return campaign
