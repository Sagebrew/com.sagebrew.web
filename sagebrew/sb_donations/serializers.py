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
    amount = serializers.IntegerField(validators=[DonationValue(), ])

    donated_for = serializers.SerializerMethodField()
    applied_to = serializers.SerializerMethodField()
    owned_by = serializers.SerializerMethodField()
    campaign = serializers.SerializerMethodField()

    def create(self, validated_data):
        request, _, _, _, _ = gather_request_data(self.context)
        donator = Pleb.get(request.user.username)
        #validated_data['owner_username'] = donator.username
        donated_towards = request.data.pop('donated_towards', [])
        campaign = validated_data.pop('campaign', None)
        donation = Donation(**validated_data).save()
        for goal in donated_towards:
            goal = Goal.nodes.get(object_uuid=goal)
            goal.donations.connect(donation)
            donation.donated_for.connect(goal)
        campaign.donations.connect(donation)
        donation.campaign.connect(campaign)
        donator.donations.connect(donation)
        donation.owned_by.connect(donator)
        donator.refresh()
        cache.set(donator.username, donator)
        return donation

    def get_donated_for(self, obj):
        return Donation.get_donated_for(obj.object_uuid)

    def get_applied_to(self, obj):
        return Donation.get_applied_to(obj.object_uuid)

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
