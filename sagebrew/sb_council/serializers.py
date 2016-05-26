import pytz
from datetime import datetime

from django.conf import settings

from neomodel import db
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.utils import spawn_task
from sb_base.serializers import (ContentSerializer, IntercomMessageSerializer,
                                 IntercomEventSerializer)
from sb_missions.serializers import MissionSerializer
from plebs.neo_models import Pleb

from .tasks import update_closed_task


class CouncilVoteSerializer(ContentSerializer):
    content = serializers.CharField(required=False)
    vote_type = serializers.BooleanField(required=True, write_only=True)
    reason = serializers.CharField(required=False, allow_blank=True,
                                   write_only=True)

    def update(self, instance, validated_data):
        pleb = validated_data.get('pleb', None)
        vote_type = validated_data.get('vote_type', None)
        query = 'MATCH (s:SBContent {object_uuid:"%s"})-[:COUNCIL_VOTE]->' \
                '(p:Pleb) RETURN p' % instance.object_uuid
        res, _ = db.cypher_query(query)
        if not res:
            instance.initial_vote_time = datetime.now(pytz.utc)
            instance.save()
        res = instance.council_vote(vote_type, pleb)
        spawn_task(task_func=update_closed_task,
                   task_param={'object_uuid': instance.object_uuid})
        return res


class MissionReviewSerializer(MissionSerializer):
    '''
    Using this serializer in place of the traditional MissionSerializer due
    to the operations being performed on the Mission being restricted to our
    admins (us) currently. In the MissionSerializer we have a check for
    verifying the person modifying the Mission is actually the owner.
    I think it is cleaner to have a different serializer for this purpose
    rather than adding in a check there to determine if it is the owner of
    the Mission or us modifying it.
    '''
    def validate(self, validated_data):
        request = self.context.get('request', '')
        if not request:
            raise ValidationError("You are not authorized to access this.")
        if request.user.username != 'tyler_wiersing' \
                and request.user.username != 'devon_bleibtrey':
            raise ValidationError("You are not authorized to access this.")
        return validated_data

    def update(self, instance, validated_data):
        owner = Pleb.get(instance.owner_username)
        prev_feedback = instance.review_feedback
        instance.review_feedback = validated_data.pop('review_feedback',
                                                      instance.review_feedback)
        if prev_feedback != instance.review_feedback and not instance.active:
            problem_string = ""
            for item in instance.review_feedback:
                problem_string += \
                    "* %s\n" % (dict(settings.REVIEW_FEEDBACK_OPTIONS)[item])
            message_body = 'Hi %s,\n\nWe have reviewed your Mission, %s, and ' \
                           'have found no problems.\nCongratulations!\n ' \
                           'We have taken your Mission live for you ' \
                           'and you can now receive Donations and Volunteers.' \
                           % (owner.first_name, instance.title)
            if problem_string:
                message_body = 'Hi %s,\nWe have reviewed your Mission, %s, ' \
                               'and found a few issues you should take care ' \
                               'of before taking your Mission live:\n\n%s' % \
                               (owner.first_name, instance.title,
                                problem_string)
            else:
                instance.active = True

            message_data = {
                'message_type': 'email',
                'subject': 'Mission Review Update',
                'body': message_body,
                'template': "personal",
                'from_user': {
                    'type': "admin",
                    'id': settings.INTERCOM_ADMIN_ID_DEVON},
                'to_user': {
                    'type': "user",
                    'user_id': instance.owner_username}
            }
            serializer = IntercomMessageSerializer(data=message_data)
            if serializer.is_valid():
                serializer.save()
        if not instance.review_feedback:
            instance.active = True
            serializer = IntercomEventSerializer(
                data={'event_name': "take-mission-live",
                      'username': instance.owner_username})
            # Don't raise an error because we rather not notify intercom than
            # hold up the mission activation process
            if serializer.is_valid():
                serializer.save()

        return instance.save()
