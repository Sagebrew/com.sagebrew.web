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
from sb_locations.serializers import LocationSerializer

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
    location_name = serializers.CharField()
    focus_name = serializers.CharField()
    focus_formal_name = serializers.CharField(read_only=True)

    url = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()
    focused_on = serializers.SerializerMethodField()
    rendered_epic = serializers.SerializerMethodField()
    # total_donation_amount = serializers.SerializerMethodField()
    # total_pledge_vote_amount = serializers.SerializerMethodField()
    # target_goal_donation_requirement = serializers.SerializerMethodField()
    # target_goal_pledge_vote_requirement = serializers.SerializerMethodField()

    district = serializers.CharField(write_only=True, allow_null=True)
    level = serializers.ChoiceField(required=True, choices=[
        ('local', "Local"), ('state', "State"),
        ('federal', "Federal")])
    sector = serializers.ChoiceField(required=True, choices=[
        ('local', "Local"), ('state_upper', "State Upper"),
        ('state_lower', "State Lower"),
        ('federal', "Federal")], allow_null=True)
    location = serializers.SerializerMethodField()

    def create(self, validated_data):
        from logging import getLogger
        logger = getLogger("loggly_logs")
        request, _, _, _, _ = gather_request_data(self.context)
        focus_type = validated_data.get('focus_on_type')
        level = validated_data.get('level')
        location = validated_data.get('location_name')
        focused_on = validated_data.get('focus_name')
        district = validated_data.get('district')
        sector = validated_data.get('sector', "")
        owner_username = request.user.username
        mission = Mission(owner_username=owner_username, sector=sector,
                          level=level).save()
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
                        '(mission)<-[:EMBARKS_ON]-(quest), ' \
                        '(location)<-[:WITHIN]-(mission) RETURN mission' % (
                            location, focused_on, level, mission.object_uuid,
                            owner_username)
                logger.critical(query)
                logger.critical(level)
                logger.critical(location)
                logger.critical(district)
                res, _ = db.cypher_query(query)
                return Mission.inflate(res.one)
            elif level == "state":
                if district:
                    add_district = '-[:ENCOMPASSES]->' \
                                   '(c:Location {name: "%s", sector: "%s"})' \
                                   '' % (district, sector)
                else:
                    add_district = ""
                query = 'MATCH (a:Location {name: ' \
                        '"United States of America"})-[:ENCOMPASSES]->' \
                        '(b:Location {name: "%s"})%s-[:POSITIONS_AVAILABLE]->' \
                        '(position:Position {name: "%s", level: "%s"}) ' \
                        'WITH position ' \
                        'MATCH (mission:Mission {object_uuid: "%s"}) ' \
                        'WITH position, mission ' \
                        'MATCH (quest:Quest {owner_username: "%s"}) ' \
                        'WITH position, mission, quest' \
                        'CREATE UNIQUE (position)' \
                        '<-[:FOCUSED_ON]-(mission)<-[:EMBARKS_ON]-' \
                        '(quest) RETURN mission' % (
                            location, add_district, focused_on, level,
                            mission.object_uuid, owner_username)
                logger.critical(query)
                logger.critical(level)
                logger.critical(location)
                logger.critical(district)
                res, _ = db.cypher_query(query)
                # Since there the deepest location is dynamic I moved this out
                # to reduce complexity on storing the location variable within
                # the query and accessing it in the CREATE UNIQUE call.
                # May be able to optimize and combine at some point.
                query = 'MATCH (mission:Mission {object_uuid: "%s"})-' \
                        '[:FOCUSED_ON]->(position:Position)' \
                        '<-[:POSITIONS_AVAILABLE]-(location:Location) ' \
                        'CREATE UNIQUE (mission)-[:WITHIN]->(location)' \
                        'RETURN mission' % mission.object_uuid
                res, _ = db.cypher_query(query)
                return Mission.inflate(res.one)
            elif level == "federal":
                if location and focused_on != "President":
                    # We need to ignore this if the President is selected
                    # since it's the only position that comes off of the
                    # USA
                    add_location = '-[:ENCOMPASSES]->' \
                                   '(b:Location {name: "%s"})' % location
                else:
                    add_location = ""
                if district and focused_on != "President" and focused_on \
                        != "Senator":
                    add_district = '-[:ENCOMPASSES]->' \
                                   '(c:Location {name: "%s", sector: "%s"})' \
                                   '' % (district, sector)
                else:
                    add_district = ""
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
                logger.critical(query)
                logger.critical(level)
                logger.critical(location)
                logger.critical(district)
                res, _ = db.cypher_query(query)
                # Since there the deepest location is dynamic I moved this out
                # to reduce complexity on storing the location variable within
                # the query and accessing it in the CREATE UNIQUE call.
                # May be able to optimize and combine at some point.
                query = 'MATCH (mission:Mission {object_uuid: "%s"})-' \
                        '[:FOCUSED_ON]->(position:Position)' \
                        '<-[:POSITIONS_AVAILABLE]-(location:Location) ' \
                        'CREATE UNIQUE (mission)-[:WITHIN]->(location) ' \
                        'RETURN mission' % mission.object_uuid
                res, _ = db.cypher_query(query)
                return Mission.inflate(res.one)
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

    def get_location(self, obj):
        location = obj.get_location()
        if location is not None:
            return LocationSerializer(location).data
        else:
            return None

    def get_focused_on(self, obj):
        return obj.get_focused_on()
