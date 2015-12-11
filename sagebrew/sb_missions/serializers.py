from datetime import datetime
import pytz
import markdown

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import db

from api.utils import gather_request_data
from api.serializers import SBSerializer
from sb_locations.serializers import LocationSerializer

from .neo_models import Mission


class MissionSerializer(SBSerializer):
    biography = serializers.CharField(required=False, max_length=255)
    epic = serializers.CharField(required=False, allow_blank=True)
    focus_on_type = serializers.ChoiceField(required=True, choices=[
        ('position', "Public Office"), ('advocacy', "Advocacy"),
        ('question', "Question")])
    facebook = serializers.CharField(required=False, allow_blank=True)
    linkedin = serializers.CharField(required=False, allow_blank=True)
    youtube = serializers.CharField(required=False, allow_blank=True)
    twitter = serializers.CharField(required=False, allow_blank=True)
    website = serializers.CharField(required=False, allow_blank=True)
    wallpaper_pic = serializers.CharField(required=False)
    title = serializers.CharField(required=False)
    owner_username = serializers.CharField(read_only=True)
    location_name = serializers.CharField()
    focus_name = serializers.CharField()
    focus_formal_name = serializers.CharField(read_only=True)

    url = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()
    focused_on = serializers.SerializerMethodField()
    rendered_epic = serializers.SerializerMethodField()

    district = serializers.CharField(write_only=True, allow_null=True)
    level = serializers.ChoiceField(required=False, choices=[
        ('local', "Local"), ('state_upper', "State Upper"),
        ('state_lower', "State Lower"),
        ('federal', "Federal")])
    location = serializers.SerializerMethodField()

    def create(self, validated_data):
        request, _, _, _, _ = gather_request_data(self.context)
        add_location = ""
        add_district = ""
        focus_type = validated_data.get('focus_on_type')
        level = validated_data.get('level')
        location = validated_data.get('location_name')
        focused_on = validated_data.get('focus_name')
        district = validated_data.get('district')
        owner_username = request.user.username
        mission = Mission(owner_username=owner_username, level=level,
                          focus_on_type=focus_type).save()
        within_query = 'MATCH (mission:Mission {object_uuid: "%s"})-' \
                       '[:FOCUSED_ON]->(position:Position)' \
                       '<-[:POSITIONS_AVAILABLE]-(location:Location) ' \
                       'CREATE UNIQUE (mission)-[:WITHIN]->(location) ' \
                       'RETURN mission' % mission.object_uuid
        if focus_type == "position":
            if level == "local":
                query = 'MATCH (location:Location {external_id: "%s"})-' \
                        '[:POSITIONS_AVAILABLE]->' \
                        '(position:Position {name: "%s", level: "%s"}) ' \
                        'WITH position, location ' \
                        'MATCH (mission:Mission {object_uuid: "%s"}) ' \
                        'WITH position, location, mission ' \
                        'MATCH (quest:Quest {owner_username: "%s"}) ' \
                        'WITH position, location, mission, quest ' \
                        'CREATE UNIQUE (position)<-[:FOCUSED_ON]-' \
                        '(mission)<-[:EMBARKS_ON]-(quest) ' \
                        'WITH quest, location, mission, position ' \
                        'CREATE UNIQUE (location)<-[:WITHIN]-(mission) ' \
                        'RETURN mission' % (
                            location, focused_on, level, mission.object_uuid,
                            owner_username)
                res, _ = db.cypher_query(query)
                return Mission.inflate(res.one)
            elif level == "state_upper" or level == "state_lower":
                if district:
                    add_district = '-[:ENCOMPASSES]->' \
                                   '(c:Location {name: "%s", sector: "%s"})' \
                                   '' % (district, level)
                # use sector for level input since we're talking about
                # state_upper and state_lower with the position
                # and level input here only has state, federal, and local
                query = 'MATCH (a:Location {name: ' \
                        '"United States of America"})-[:ENCOMPASSES]->' \
                        '(b:Location {name: "%s"})%s-[:POSITIONS_AVAILABLE]->' \
                        '(position:Position {name: "%s", level: "%s"}) ' \
                        'WITH position ' \
                        'MATCH (mission:Mission {object_uuid: "%s"}) ' \
                        'WITH position, mission ' \
                        'MATCH (quest:Quest {owner_username: "%s"}) ' \
                        'WITH position, mission, quest' \
                        ' CREATE UNIQUE (position)' \
                        '<-[:FOCUSED_ON]-(mission)<-[:EMBARKS_ON]-' \
                        '(quest) RETURN mission' % (
                            location, add_district, focused_on, level,
                            mission.object_uuid, owner_username)
                res, _ = db.cypher_query(query)
                # Since there the deepest location is dynamic I moved this out
                # to reduce complexity on storing the location variable within
                # the query and accessing it in the CREATE UNIQUE call.
                # May be able to optimize and combine at some point.
                res, _ = db.cypher_query(within_query)
                return Mission.inflate(res.one)
            elif level == "federal":
                if location and focused_on != "President":
                    # We need to ignore this if the President is selected
                    # since it's the only position that comes off of the
                    # USA
                    add_location = '-[:ENCOMPASSES]->' \
                                   '(b:Location {name: "%s"})' % location
                if district and focused_on != "President" and focused_on \
                        != "Senator":
                    add_district = '-[:ENCOMPASSES]->' \
                                   '(c:Location {name: "%s", sector: "%s"})' \
                                   '' % (district, level)
                query = 'MATCH (a:Location {name: ' \
                        '"United States of America"})%s%s' \
                        '-[:POSITIONS_AVAILABLE]->' \
                        '(position:Position {name: "%s", level: "%s"}) ' \
                        'WITH position ' \
                        'MATCH (quest:Quest {owner_username: "%s"}) ' \
                        'WITH quest, position ' \
                        'MATCH (mission:Mission {object_uuid: "%s"}) ' \
                        'WITH quest, position, mission ' \
                        'CREATE UNIQUE (position)<-[:FOCUSED_ON]-(mission)' \
                        '<-[:EMBARKS_ON]-(quest) RETURN mission' % (
                            add_location, add_district, focused_on, level,
                            owner_username, mission.object_uuid)
                res, _ = db.cypher_query(query)
                # Since there the deepest location is dynamic I moved this out
                # to reduce complexity on storing the location variable within
                # the query and accessing it in the CREATE UNIQUE call.
                # May be able to optimize and combine at some point.
                res, _ = db.cypher_query(within_query)
                return Mission.inflate(res.one)
        elif focus_type == "advocacy":
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

    def get_location(self, obj):
        location = obj.get_location()
        if location is not None:
            return LocationSerializer(location).data
        else:
            return None

    def get_focused_on(self, obj):
        return obj.get_focused_on()
