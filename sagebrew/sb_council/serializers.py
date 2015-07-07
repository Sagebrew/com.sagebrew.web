import pytz
from datetime import datetime

from rest_framework import serializers
from sb_base.serializers import ContentSerializer

from logging import getLogger
logger = getLogger('loggly_logs')


class CouncilVoteSerializer(ContentSerializer):
    content = serializers.CharField(required=False)
    council_vote_type = serializers.BooleanField(required=True,
                                                 write_only=True)
    reason = serializers.CharField(required=False, allow_blank=True,
                                   write_only=True)

    def update(self, instance, validated_data):
        pleb = validated_data.get('pleb', None)
        current_reason = ""
        if instance.council_votes.is_connected(pleb):
            current_reason = instance.council_votes.relationship(
                pleb).reasoning
        instance.last_council_vote = datetime.now(pytz.utc)
        if instance.get_council_decision() < 0.66:
            instance.is_masked = False
        else:
            instance.is_masked = True
        instance.save()
        reason = validated_data.get('reason', current_reason)
        vote_type = validated_data.get('council_vote_type', None)
        return instance.council_vote(vote_type, pleb, reason)
