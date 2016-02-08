from django.conf import settings

from rest_framework import serializers
from rest_framework.reverse import reverse

from api.serializers import SBSerializer
from sb_missions.neo_models import Mission
from sb_missions.serializers import MissionSerializer
from plebs.neo_models import Pleb
from plebs.serializers import PlebSerializerNeo

from sb_volunteers.neo_models import Volunteer


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
