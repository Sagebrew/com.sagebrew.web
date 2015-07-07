import pytz
from datetime import datetime

from neomodel import db
from rest_framework import serializers

from api.utils import spawn_task
from sb_base.serializers import ContentSerializer

from .tasks import update_masked_task

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
        query = 'MATCH (s:SBContent {object_uuid:"%s"})-[:COUNCIL_VOTE]->' \
                '(p:Pleb) RETURN p' % instance.object_uuid
        res, _ = db.cypher_query(query)
        if not res[0].p:
            instance.initial_vote_time = datetime.now(pytz.utc)
            instance.save()
        current_reason = ""
        if instance.council_votes.is_connected(pleb):
            current_reason = instance.council_votes.relationship(
                pleb).reasoning
        instance.save()
        spawn_task(task_func=update_masked_task,
                   task_param={'object_uuid': instance.object_uuid})
        reason = validated_data.get('reason', current_reason)
        vote_type = validated_data.get('council_vote_type', None)
        return instance.council_vote(vote_type, pleb, reason)
