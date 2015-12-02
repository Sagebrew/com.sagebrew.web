from datetime import datetime
import pytz
import bleach
import markdown

from django.core.cache import cache

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import db

from api.utils import gather_request_data
from api.serializers import SBSerializer

from .neo_models import Mission


class MissionSerializer(SBSerializer):
    biography = serializers.CharField(required=False, max_length=255)
    epic = serializers.CharField(required=False, allow_blank=True)
    focus_on_type = serializers.ChoiceField(required=True, choices=[
        ('position', "Public Office"), ('tag', "Advocacy"),
        ('question', "Question")])
    facebook = serializers.CharField(required=False, allow_blank=True)
    linkedin = serializers.CharField(required=False, allow_blank=True)
    youtube = serializers.CharField(required=False, allow_blank=True)
    twitter = serializers.CharField(required=False, allow_blank=True)
    website = serializers.CharField(required=False, allow_blank=True)
    wallpaper_pic = serializers.CharField(required=False)
    title = serializers.CharField(required=False)
    owner_username = serializers.CharField(read_only=True)
    location_name = serializers.CharField(read_only=True)
    focus_name = serializers.CharField(read_only=True)
    focus_formal_name = serializers.CharField(read_only=True)

    url = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()
    focused_on = serializers.CharField(required=True, source='get_focused_on')
    rendered_epic = serializers.SerializerMethodField()
    # total_donation_amount = serializers.SerializerMethodField()
    # total_pledge_vote_amount = serializers.SerializerMethodField()
    # target_goal_donation_requirement = serializers.SerializerMethodField()
    # target_goal_pledge_vote_requirement = serializers.SerializerMethodField()

    district = serializers.CharField(write_only=True)
    level = serializers.ChoiceField(required=True, choices=[
        ('local', "Local"), ('state', "State"),
        ('federal', "Federal")])
    location = serializers.CharField(required=True, source='get_location')

    def create(self, validated_data):
        request, _, _, _, _ = gather_request_data(self.context)
        focus_type = validated_data.get('focus_on_type')
        level = validated_data.get('level')
        location = validated_data.get('location')
        focused_on = validated_data.get('focused_on')
        district = validated_data.get('district')
        mission = Mission(owner_username=request.user.username).save()
        if focus_type == "position":
            if level == "local":
                query = 'MATCH (a:Location {external_id: "%s"})-' \
                        '[POSITIONS_AVAILABLE]->' \
                        '(b:Position {name: "%s", level: "%s"}) ' \
                        'CREATE UNIQUE (b)<-[FOCUSED_ON]-' \
                        '(m:Mission {object_uuid: "%s"}) RETURN b' % (
                            location, focused_on, level, mission.object_uuid)
                res, _ = db.cypher_query(query)
            elif level == "state":
                if district:
                    add_district = '-[ENCOMPASSES]->' \
                                   '(c:Location {name: "%s"})' % district
                else:
                    add_district = ""
                query = 'MATCH (a:Location {name: ' \
                        '"United States of America"})-[ENCOMPASSES]->' \
                        '(b:Location {name: "%s"})%s-[POSITIONS_AVAILABLE]->' \
                        '(d:Position {name: "%s", level: "%s"}) ' \
                        'CREATE UNIQUE (d)<-[FOCUSED_ON]-(m:Mission ' \
                        '{object_uuid: "%s"}) RETURN d' % (
                            location, add_district, focused_on, level,
                            mission.object_uuid)
                res, _ = db.cypher_query(query)
            elif level == "federal":
                if location:
                    add_location = '-[ENCOMPASSES]->' \
                                   '(c:Location {name: "%s"})' % location
                else:
                    add_location = ""
                if district:
                    add_district = '-[ENCOMPASSES]->' \
                                   '(c:Location {name: "%s"})' % district
                else:
                    add_district = ""
                query = 'MATCH (a:Location {name: ' \
                        '"United States of America"})%s%s' \
                        '-[POSITIONS_AVAILABLE]->' \
                        '(d:Position {name: "%s", level: "%s"}) ' \
                        'CREATE UNIQUE (d)<-[FOCUSED_ON]-(m:Mission ' \
                        '{object_uuid: "%s"}) RETURN d' % (
                            add_location, add_district, focused_on, level,
                            mission.object_uuid)
                res, _ = db.cypher_query(query)
        elif focus_type == "tag":
            # Need to handle potential district with location
            pass
        elif focus_type == "question":
            pass
        else:
            return False

        return mission

    def update(self, instance, validated_data):
        instance.title = validated_data.pop('title', instance.title)
        instance.content = validated_data.pop('content', instance.content)
        instance.last_edited_on = datetime.now(pytz.utc)
        instance.save()
        return instance

    def get_href(self, obj):
        return reverse('mission-detail',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=self.context.get('request', None))

    def get_url(self, obj):
        return ""

    def get_rendered_epic(self, obj):
        if obj.epic is not None:
            return markdown.markdown(obj.epic.replace('&gt;', '>'))
        else:
            return ""
