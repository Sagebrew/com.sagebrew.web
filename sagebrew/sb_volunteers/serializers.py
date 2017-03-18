from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from django.utils.text import slugify

from rest_framework import serializers
from rest_framework.reverse import reverse

from sagebrew.api.serializers import SBSerializer
from sagebrew.sb_base.serializers import IntercomMessageSerializer
from sagebrew.sb_missions.neo_models import Mission
from sagebrew.sb_missions.serializers import MissionSerializer
from sagebrew.plebs.neo_models import Pleb
from sagebrew.plebs.serializers import PlebSerializerNeo

from sagebrew.sb_volunteers.neo_models import Volunteer


class VolunteerSerializer(SBSerializer):
    """
    This serializer is for handling a user volunteering to do something
    for a mission.
    """
    activities = serializers.MultipleChoiceField(
        choices=settings.VOLUNTEER_ACTIVITIES)
    href = serializers.SerializerMethodField()
    volunteer = serializers.SerializerMethodField()
    mission = serializers.SerializerMethodField()

    def create(self, validated_data):
        volunteer = validated_data.pop('volunteer', None)
        mission = validated_data.pop('mission', None)
        activity = Volunteer(mission_id=mission.object_uuid,
                             **validated_data).save()
        activity.volunteer.connect(volunteer)
        activity.mission.connect(mission)
        mission_owner = Pleb.get(username=mission.owner_username)
        message_data = {
            'message_type': 'email',
            'subject': 'New Volunteer',
            'body': get_template('volunteer/email/new_volunteer.html').render(
                Context({
                    'first_name': mission_owner.first_name,
                    'mission_title': mission.get_mission_title(),
                    "activities": [dict(settings.VOLUNTEER_ACTIVITIES)[item]
                                   for item in validated_data['activities']],
                    "volunteer_first_name": volunteer.first_name,
                    "volunteer_last_name": volunteer.last_name,
                    "mission_volunteers": reverse(
                        'mission_volunteers',
                        kwargs={
                            'object_uuid': mission.object_uuid,
                            'slug': slugify(mission.get_mission_title())},
                        request=self.context.get('request'))
                })),
            'template': "personal",
            'from_user': {
                'type': "admin",
                'id': settings.INTERCOM_ADMIN_ID_DEVON
            },
            'to_user': {
                'type': "user",
                'user_id': mission.owner_username
            }
        }
        serializer = IntercomMessageSerializer(data=message_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return activity

    def update(self, instance, validated_data):
        instance.activities = validated_data.get('activities',
                                                 instance.activities)
        instance.save()
        return instance

    def get_href(self, obj):
        request = self.context.get('request', None)
        return reverse('volunteer-detail',
                       kwargs={'volunteer_id': obj.object_uuid,
                               'object_uuid': obj.mission_id}, request=request)

    def get_mission(self, obj):
        request = self.context.get('request', None)
        return MissionSerializer(Mission.get(
            obj.mission_id), context={'request': request}).data

    def get_volunteer(self, obj):
        request = self.context.get('request', None)
        return PlebSerializerNeo(Pleb.get(obj.owner_username),
                                 context={'request': request}).data
