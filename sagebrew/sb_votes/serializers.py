from rest_framework import serializers

from api.serializers import SBSerializer


class VoteSerializer(SBSerializer):
    # Need to add validator here or in Votable Content that limits the amount
    # of flags that can be placed on a piece of content from a single user to
    # one
    vote_type = serializers.BooleanField()
    url = serializers.SerializerMethodField()
    vote_on = serializers.SerializerMethodField()

    def create(self, validated_data):
        return None

    def update(self, instance, validated_data):
        return None
