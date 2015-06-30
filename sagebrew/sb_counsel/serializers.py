from rest_framework import serializers

from logging import getLogger
logger = getLogger('loggly_logs')


class CounselVoteSerializer(serializers.Serializer):
    counsel_vote_type = serializers.BooleanField(required=True,
                                                 write_only=True)
    reason = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        pleb = validated_data.get('pleb', None)
        current_reason = ""
        if instance.counsel_votes.is_connected(pleb):
            current_reason = instance.counsel_votes.relationship(
                pleb).reasoning
        reason = validated_data.get('reason', current_reason)
        vote_type = validated_data.get('counsel_vote_type', None)
        return instance.counsel_vote(vote_type, pleb, reason)
