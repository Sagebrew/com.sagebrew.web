import markdown

from django.core.cache import cache
from django.utils.text import slugify
from django.conf import settings

from rest_framework import serializers, status
from rest_framework.reverse import reverse
from rest_framework.exceptions import ValidationError

from neomodel import db, DoesNotExist

from api.utils import gather_request_data
from api.serializers import SBSerializer
from sb_locations.serializers import LocationSerializer
from sb_tags.neo_models import Tag
from sb_search.utils import remove_search_object

from .neo_models import Mission


class MissionSerializer(SBSerializer):
    active = serializers.BooleanField(required=False)
    completed = serializers.BooleanField(required=False)
    about = serializers.CharField(required=False, allow_blank=True,
                                  max_length=255)
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
    title = serializers.CharField(max_length=140, required=False,
                                  allow_blank=True)
    owner_username = serializers.CharField(read_only=True)
    location_name = serializers.CharField()
    focus_name = serializers.CharField()
    focus_formal_name = serializers.CharField(read_only=True)

    url = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()
    focused_on = serializers.SerializerMethodField()
    rendered_epic = serializers.SerializerMethodField()
    is_editor = serializers.SerializerMethodField()
    is_moderator = serializers.SerializerMethodField()
    quest = serializers.SerializerMethodField()
    focus_name_formatted = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    total_donation_amount = serializers.SerializerMethodField()
    district = serializers.CharField(write_only=True, allow_null=True)
    level = serializers.ChoiceField(required=False, choices=[
        ('local', "Local"), ('state_upper', "State Upper"),
        ('state_lower', "State Lower"),
        ('federal', "Federal"), ('state', "State")])
    location = serializers.SerializerMethodField()

    def create(self, validated_data):
        from sb_quests.neo_models import Quest, Position
        request, _, _, _, _ = gather_request_data(self.context)
        query = 'MATCH (quest:Quest {owner_username: "%s"})-[:EMBARKS_ON]->' \
                '(mission:Mission) ' \
                'RETURN quest, ' \
                'count(mission) as mission_count' % request.user.username
        res, _ = db.cypher_query(query)
        if res.one is not None:
            quest = Quest.inflate(res.one['quest'])
            if quest.account_type != "paid":
                if res.one['mission_count'] >= settings.FREE_MISSIONS:
                    raise ValidationError(
                        detail={"detail": "Sorry free Quests can only "
                                          "have 5 Missions.",
                                "developer_message": "",
                                "status_code": status.HTTP_400_BAD_REQUEST})
        add_location = ""
        add_district = ""
        verified = validated_data.get('verified')
        focus_type = validated_data.get('focus_on_type')
        level = validated_data.get('level')
        location = validated_data.get('location_name')
        focused_on = validated_data.get('focus_name')
        district = validated_data.get('district')
        # TODO what happens if a moderator makes the mission?
        owner_username = request.user.username
        title = focused_on.title().replace('-', ' ').replace('_', ' ')
        mission = Mission(owner_username=owner_username, level=level,
                          focus_on_type=focus_type,
                          focus_name=focused_on,
                          title=title).save()
        within_query = 'MATCH (mission:Mission {object_uuid: "%s"})-' \
                       '[:FOCUSED_ON]->(position:Position)' \
                       '<-[:POSITIONS_AVAILABLE]-(location:Location) ' \
                       'CREATE UNIQUE (mission)-[:WITHIN]->(location) ' \
                       'RETURN mission' % mission.object_uuid
        if focus_type == "position":
            if not verified:
                query = 'MATCH (location:Location {external_id:"%s"})-' \
                        '[:POSITIONS_AVAILABLE]->(position:Position ' \
                        '{name:"%s", level:"%s"}) RETURN position' % \
                        (location, focused_on, level)
                res, _ = db.cypher_query(query)
                if not res.one:
                    focused_on = focused_on.title().replace('-', ' ')\
                        .replace('_', ' ')
                    new_position = Position(verified=False, name=focused_on,
                                            level=level,
                                            user_created=True).save()
                    query = 'MATCH (location:Location {external_id: "%s"}), ' \
                            '(position:Position {object_uuid:"%s"}) ' \
                            'WITH location, position ' \
                            'CREATE UNIQUE (position)' \
                            '<-[r:POSITIONS_AVAILABLE]-(location), ' \
                            '(position)-[:AVAILABLE_WITHIN]->(location) ' \
                            'RETURN position' % (location,
                                                 new_position.object_uuid)
                    res, _ = db.cypher_query(query)
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
                # Since the deepest location is dynamic I moved this out
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
            focused_on = '-'.join(focused_on.replace('_', '-').lower().split())
            try:
                Tag.nodes.get(name=focused_on)
            except (DoesNotExist, Tag.DoesNotExist):
                Tag(name=focused_on).save()
            if level == "local":
                query = 'MATCH (tag:Tag {name: "%s"}) ' \
                        'WITH tag ' \
                        'MATCH (location:Location {external_id: "%s"}) ' \
                        'WITH tag, location ' \
                        'MATCH (quest:Quest {owner_username: "%s"}) ' \
                        'WITH tag, location, quest ' \
                        'MATCH (mission:Mission {object_uuid: "%s"}) ' \
                        'WITH tag, location, quest, mission ' \
                        'CREATE UNIQUE (tag)<-[:FOCUSED_ON]-(mission)' \
                        '<-[:EMBARKS_ON]-(quest) WITH location, mission ' \
                        'CREATE UNIQUE (mission)-[:WITHIN]->(location)' \
                        'RETURN mission' % (focused_on, location,
                                            owner_username, mission.object_uuid)
                res, _ = db.cypher_query(query)
                return Mission.inflate(res.one)
            elif level == "state":
                if district:
                    loc_query = 'MATCH (:Location {name: ' \
                                '"United States of America"})' \
                                '-[:ENCOMPASSES]->(:Location {name: "%s"})' \
                                '-[:ENCOMPASSES]->(location:Location ' \
                                '{name: "%s", sector: "federal"}) ' \
                                'WITH location, mission, ' \
                                'tag, quest' % (location, district)
                else:
                    loc_query = 'MATCH (:Location {name: ' \
                                '"United States of America"})' \
                                '-[:ENCOMPASSES]->' \
                                '(location:Location {name: "%s"}) ' \
                                'WITH location, mission, ' \
                                'tag, quest' % location
                # TODO same as federal
                query = 'MATCH (tag:Tag {name: "%s"}) ' \
                        'WITH tag ' \
                        'MATCH (quest:Quest {owner_username: "%s"}) ' \
                        'WITH tag, quest ' \
                        'MATCH (mission:Mission {object_uuid: "%s"}) ' \
                        'WITH tag, quest, mission ' \
                        '%s ' \
                        'CREATE UNIQUE (tag)<-[:FOCUSED_ON]-(mission)' \
                        '<-[:EMBARKS_ON]-(quest) ' \
                        'WITH mission, location ' \
                        'CREATE UNIQUE (mission)-[:WITHIN]->(location) ' \
                        'RETURN mission' % (focused_on, owner_username,
                                            mission.object_uuid, loc_query)
                res, _ = db.cypher_query(query)
                return Mission.inflate(res.one)
            elif level == "federal":
                if district:
                    loc_query = 'MATCH (:Location {name: ' \
                                '"United States of America"})' \
                                '-[:ENCOMPASSES]->(:Location {name: "%s"})' \
                                '-[:ENCOMPASSES]->(location:Location ' \
                                '{name: "%s", sector: "federal"}) ' \
                                'WITH location, mission, ' \
                                'tag, quest' % (location, district)
                elif location:
                    loc_query = 'MATCH (:Location {name: ' \
                                '"United States of America"})' \
                                '-[:ENCOMPASSES]->' \
                                '(location:Location {name: "%s"}) ' \
                                'WITH location, mission, ' \
                                'tag, quest' % location
                else:
                    loc_query = 'MATCH (location:Location {name: ' \
                                '"United States of America"}) ' \
                                'WITH location, mission, tag, quest'
                # TODO same as state
                query = 'MATCH (tag:Tag {name: "%s"}) ' \
                        'WITH tag ' \
                        'MATCH (quest:Quest {owner_username: "%s"}) ' \
                        'WITH tag, quest ' \
                        'MATCH (mission:Mission {object_uuid: "%s"}) ' \
                        'WITH tag, quest, mission ' \
                        '%s ' \
                        'CREATE UNIQUE (tag)<-[:FOCUSED_ON]-(mission)' \
                        '<-[:EMBARKS_ON]-(quest) ' \
                        'WITH mission, location ' \
                        'CREATE UNIQUE (mission)-[:WITHIN]->(location) ' \
                        'RETURN mission' % (focused_on, owner_username,
                                            mission.object_uuid, loc_query)
                res, _ = db.cypher_query(query)
        elif focus_type == "question":
            return None
        else:
            return None
        return mission

    def update(self, instance, validated_data):
        initial_state = instance.active
        instance.active = validated_data.pop('active', instance.active)
        if initial_state is True and instance.active is False:
            remove_search_object(instance.object_uuid, 'mission')
        instance.completed = validated_data.pop(
            'completed', instance.completed)
        instance.title = validated_data.pop('title', instance.title)
        about = validated_data.get('about', instance.about)
        if about is not None:
            about = about.strip()
            if about == "":
                about = None
        instance.about = about
        instance.epic = validated_data.pop('epic', instance.epic)
        instance.facebook = validated_data.pop('facebook', instance.facebook)
        instance.linkedin = validated_data.pop('linkedin', instance.linkedin)
        instance.youtube = validated_data.pop('youtube', instance.youtube)
        instance.twitter = validated_data.pop('twitter', instance.twitter)
        website = validated_data.get('website', instance.website)
        if website is None:
            instance.website = website
        elif "https://" in website or "http://" in website:
            instance.website = website
        else:
            if website.strip() == "":
                instance.website = None
            else:
                instance.website = "http://" + website
        instance.wallpaper_pic = validated_data.pop('wallpaper_pic',
                                                    instance.wallpaper_pic)
        instance.save()
        cache.set("%s_mission" % instance.object_uuid, instance)
        if instance.active:
            return super(MissionSerializer, self).update(
                instance, validated_data)
        return instance

    def get_href(self, obj):
        return reverse('mission-detail',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=self.context.get('request', None))

    def get_url(self, obj):
        return reverse('mission',
                       kwargs={'object_uuid': obj.object_uuid,
                               'slug': slugify(obj.get_mission_title())},
                       request=self.context.get('request', None))

    def get_rendered_epic(self, obj):
        if obj.epic is not None:
            return markdown.markdown(obj.epic.replace('&gt;', '>'))
        else:
            return ""

    def get_location(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        location = obj.get_location()
        if location is not None:
            return LocationSerializer(location,
                                      context={'request': request}).data
        else:
            return None

    def get_focused_on(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return obj.get_focused_on(request=request)

    def get_quest(self, obj):
        from sb_quests.neo_models import Quest
        from sb_quests.serializers import QuestSerializer
        request, _, _, _, _ = gather_request_data(self.context)
        query = 'MATCH (quest:Quest)-[:EMBARKS_ON]->' \
                '(:Mission {object_uuid: "%s"}) RETURN quest' % obj.object_uuid
        res, _ = db.cypher_query(query)
        if res.one is None:
            return None
        return QuestSerializer(Quest.inflate(res.one),
                               context={'request': request}).data

    def get_focus_name_formatted(self, obj):
        if obj.focus_name is not None:
            return obj.focus_name.title().replace('-', ' ').replace('_', ' ')
        return obj.focus_name

    def get_is_editor(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        if request is None:
            return None
        return request.user.username in Mission.get_editors(obj.owner_username)

    def get_is_moderator(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        if request is None:
            return None
        return request.user.username in Mission.get_moderators(
            obj.owner_username)

    def get_slug(self, obj):
        return slugify(obj.get_mission_title())

    def get_total_donation_amount(self, obj):
        return obj.get_total_donation_amount()
