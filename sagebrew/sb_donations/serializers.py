from rest_framework import serializers


class DonationSerializer(serializers.Serializer):
    completed = serializers.BooleanField()
    amount = serializers.IntegerField()

    donated_for = serializers.SerializerMethodField()
    applied_to = serializers.SerializerMethodField()
    owned_by = serializers.SerializerMethodField()
    campaign = serializers.SerializerMethodField()

    def get_donated_for(self, obj):
        pass

    def get_applied_to(self, obj):
        pass

    def get_owned_by(self, obj):
        pass

    def get_campaign(self, obj):
        pass