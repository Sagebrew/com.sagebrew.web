from django.core.cache import cache
from django.utils.text import slugify
from django.conf import settings
from django.templatetags.static import static

from rest_framework import serializers, status
from rest_framework.reverse import reverse

from neomodel import db, DoesNotExist

from api.utils import (gather_request_data, clean_url, empty_text_to_none,
                       smart_truncate, render_content)
from api.serializers import SBSerializer

from sb_base.serializers import IntercomEventSerializer
from sb_locations.serializers import LocationSerializer
from sb_tags.neo_models import Tag
from sb_search.utils import remove_search_object

from .neo_models import Mission
from .utils import setup_onboarding

class MissionSerializer(SBSerializer):
    active = serializers.BooleanField(required=False)
    completed = serializers.BooleanField(required=False)
    about = serializers.CharField(required=False, allow_blank=True,
                                  max_length=255)
    epic = serializers.CharField(required=False, allow_blank=True)
    focus_on_type = serializers.ChoiceField(required=True, choices=[
        ('position', "Public Office"), ('advocacy', "Advocacy"),
        ('question', "Question")])
    facebook = serializers.URLField(required=False, allow_blank=True)
    linkedin = serializers.URLField(required=False, allow_blank=True)
    youtube = serializers.URLField(required=False, allow_blank=True)
    twitter = serializers.URLField(required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True)
    wallpaper_pic = serializers.CharField(required=False)
    title = serializers.CharField(max_length=240, required=False,
                                  allow_blank=True)
    owner_username = serializers.CharField(read_only=True)
    location_name = serializers.CharField(required=False, allow_null=True)
    focus_name = serializers.CharField(max_length=240)
    focus_formal_name = serializers.CharField(read_only=True)

    url = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()
    focused_on = serializers.SerializerMethodField()
    rendered_epic = serializers.SerializerMethodField()
    is_editor = serializers.SerializerMethodField()
    is_moderator = serializers.SerializerMethodField()
    has_endorsed_quest = serializers.SerializerMethodField()
    has_endorsed_profile = serializers.SerializerMethodField()
    quest = serializers.SerializerMethodField()
    focus_name_formatted = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    total_donation_amount = serializers.SerializerMethodField()
    district = serializers.CharField(write_only=True, allow_null=True)
    level = serializers.ChoiceField(required=False, choices=[
        ('local', "Local"), ('state_upper', "State Upper"),
        ('state_lower', "State Lower"),
        ('federal', "Federal"), ('state', "State")])
    level_readable = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    title_summary = serializers.SerializerMethodField()

    def create(self, validated_data):
        from sb_quests.neo_models import Quest, Position
        request, _, _, _, _ = gather_request_data(self.context)
        query = 'MATCH (quest:Quest {owner_username: "%s"}) WITH quest ' \
                'OPTIONAL MATCH (quest)-[:EMBARKS_ON]->' \
                '(mission:Mission) RETURN quest, ' \
                'count(mission) as mission_count' % request.user.username
        res, _ = db.cypher_query(query)
        if res.one is not None:
            quest = Quest.inflate(res.one['quest'])
            if quest.account_type == "free":
                if res.one['mission_count'] >= settings.FREE_MISSIONS:
                    raise serializers.ValidationError(
                        {"detail": "Sorry free Quests can only "
                                   "have 5 Missions.",
                         "developer_message": "",
                         "status_code": status.HTTP_400_BAD_REQUEST})
        else:
            raise serializers.ValidationError(
                {"detail": "We couldn't find a Quest for this "
                           "Mission. Please contact us if this "
                           "problem continues.",
                 "developer_message": "",
                 "status_code": status.HTTP_404_NOT_FOUND})
        add_district = ""
        focus_type = validated_data.get('focus_on_type')
        level = validated_data.get('level')

        # Properly Title the case of the following words in the location name
        location = validated_data.get('location_name')
        if location is not None:
            location = location.replace(
                " Of", " of").replace(" And", " and").replace(" Or", " or")
        focused_on = validated_data.get('focus_name')
        if focus_type == "advocacy":
            focused_on = slugify(focused_on)
        else:
            focused_on = slugify(
                focused_on).title().replace('-', ' ').replace('_', ' ')
        district = validated_data.get('district')
        # TODO what happens if a moderator makes the mission?
        owner_username = request.user.username
        title = focused_on.title().replace('-', ' ').replace('_', ' ')
        mission = Mission(owner_username=owner_username, level=level,
                          focus_on_type=focus_type,
                          focus_name=focused_on,
                          title=title,
                          wallpaper_pic=static(
                              'images/wallpaper_capitol_2.jpg')).save()
        if focus_type == "position":
            if level == "federal":
                if district:
                    loc_query = '(:Location {name: ' \
                                '"United States of America"})' \
                                '-[:ENCOMPASSES]->(:Location {name: "%s"})' \
                                '-[:ENCOMPASSES]->(location:Location ' \
                                '{name: "%s", sector: "federal"})' % (
                                    location, district)
                elif location and focused_on != "President":
                    loc_query = '(:Location {name: ' \
                                '"United States of America"})' \
                                '-[:ENCOMPASSES]->' \
                                '(location:Location {name: "%s"})' % location
                else:
                    loc_query = '(location:Location {name: ' \
                                '"United States of America"})'
            elif level == "state_upper" or level == "state_lower" \
                    or level == "state":
                parent_location = "location"
                if district:
                    add_district = '-[:ENCOMPASSES]->' \
                                   '(location:Location ' \
                                   '{name: "%s", sector: "%s"})' \
                                   '' % (district, level)
                    parent_location = "b"
                # use sector for level input since we're talking about
                # state_upper and state_lower with the position
                # and level input here only has state, federal, and local
                loc_query = '(a:Location {name: "United States of America"})' \
                            '-[:ENCOMPASSES]->' \
                            '(%s:Location {name: "%s"})%s' % (
                                parent_location, location, add_district)
            else:
                loc_query = '(location:Location {external_id:"%s"})' % location
            query = 'MATCH %s-' \
                    '[:POSITIONS_AVAILABLE]->(position:Position ' \
                    '{name:"%s", level:"%s"}) RETURN position' % \
                    (loc_query, focused_on, level)
            res, _ = db.cypher_query(query)
            if not res.one:
                focused_on = slugify(focused_on).title().replace('-', ' ')\
                    .replace('_', ' ')
                new_position = Position(verified=False, name=focused_on,
                                        level=level,
                                        user_created=True).save()
                query = 'MATCH %s, ' \
                        '(position:Position {object_uuid:"%s"}) ' \
                        'CREATE UNIQUE (position)' \
                        '<-[r:POSITIONS_AVAILABLE]-(location) ' \
                        'RETURN position' % (loc_query,
                                             new_position.object_uuid)
                res, _ = db.cypher_query(query)
            query = 'MATCH %s-' \
                    '[:POSITIONS_AVAILABLE]->' \
                    '(position:Position {name: "%s", level: "%s"}),' \
                    '(mission:Mission {object_uuid: "%s"}),' \
                    '(quest:Quest {owner_username: "%s"}) ' \
                    'CREATE UNIQUE (position)<-[:FOCUSED_ON]-' \
                    '(mission)<-[:EMBARKS_ON]-(quest) ' \
                    'WITH quest, location, mission, position ' \
                    'CREATE UNIQUE (location)<-[:WITHIN]-(mission) ' \
                    'RETURN mission' % (
                        loc_query, focused_on, level, mission.object_uuid,
                        owner_username)
            res, _ = db.cypher_query(query)
            mission = Mission.inflate(res.one)
        elif focus_type == "advocacy":
            focused_on = slugify(focused_on)
            try:
                Tag.nodes.get(name=focused_on)
            except (DoesNotExist, Tag.DoesNotExist):
                Tag(name=focused_on).save()
            if level == "local":
                loc_query = '(location:Location {external_id: "%s"}) ' % (
                    location)
            elif level == "state":
                if district:
                    loc_query = '(:Location {name: ' \
                                '"United States of America"})' \
                                '-[:ENCOMPASSES]->(:Location {name: "%s"})' \
                                '-[:ENCOMPASSES]->(location:Location ' \
                                '{name: "%s", sector: "federal"}) ' % (
                                    location, district)
                else:
                    loc_query = '(:Location {name: ' \
                                '"United States of America"})' \
                                '-[:ENCOMPASSES]->' \
                                '(location:Location {name: "%s"}) ' % location
            elif level == "federal":
                if district:
                    loc_query = '(:Location {name: ' \
                                '"United States of America"})' \
                                '-[:ENCOMPASSES]->(:Location {name: "%s"})' \
                                '-[:ENCOMPASSES]->(location:Location ' \
                                '{name: "%s", sector: "federal"}) ' % (
                                    location, district)
                elif location and focused_on != "President":
                    loc_query = '(:Location {name: ' \
                                '"United States of America"})' \
                                '-[:ENCOMPASSES]->' \
                                '(location:Location {name: "%s"}) ' % location
                else:
                    loc_query = '(location:Location {name: ' \
                                '"United States of America"}) '
            else:
                raise serializers.ValidationError(
                    {"detail": "Sorry Could Not Determine Where You're "
                               "advocating. Please try a different "
                               "location or contact us.",
                     "developer_message": "",
                     "status_code": status.HTTP_400_BAD_REQUEST})
            query = 'MATCH (tag:Tag {name: "%s"}), ' \
                    '(quest:Quest {owner_username: "%s"}), ' \
                    '(mission:Mission {object_uuid: "%s"}), ' \
                    '%s WITH tag, quest, mission, location ' \
                    'CREATE UNIQUE (tag)<-[:FOCUSED_ON]-(mission)' \
                    '<-[:EMBARKS_ON]-(quest) WITH location, mission ' \
                    'CREATE UNIQUE (mission)-[:WITHIN]->(location) ' \
                    'RETURN mission' % (focused_on,
                                        owner_username, mission.object_uuid,
                                        loc_query)
            res, _ = db.cypher_query(query)
            if res.one is not None:
                mission = Mission.inflate(res.one)
        from logging import getLogger
        logger = getLogger("loggly_logs")
        logger.critical("call onboarding")
        setup_onboarding(quest, mission)
        return mission

    def update(self, instance, validated_data):
        from sb_base.serializers import validate_is_owner
        validate_is_owner(self.context.get('request', None), instance)
        initial_state = instance.active
        instance.active = validated_data.pop('active', instance.active)
        if initial_state is False and instance.active is True:
            serializer = IntercomEventSerializer(
                data={'event_name': "take-mission-live",
                      'username': instance.owner_username})
            # Don't raise an error because we rather not notify intercom than
            # hold up the mission activation process
            if serializer.is_valid():
                serializer.save()
        if initial_state is True and instance.active is False:
            remove_search_object(instance.object_uuid, 'mission')
        instance.completed = validated_data.pop(
            'completed', instance.completed)
        title = validated_data.pop('title', instance.title)
        if empty_text_to_none(title) is not None:
            instance.title = title
        instance.about = empty_text_to_none(
            validated_data.get('about', instance.about))
        instance.epic = validated_data.pop('epic', instance.epic)
        instance.facebook = clean_url(
            validated_data.get('facebook', instance.facebook))
        instance.linkedin = clean_url(
            validated_data.get('linkedin', instance.linkedin))
        instance.youtube = clean_url(
            validated_data.get('youtube', instance.youtube))
        instance.twitter = clean_url(
            validated_data.get('twitter', instance.twitter))
        instance.website = clean_url(
            validated_data.get('website', instance.website))
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
        return render_content(obj.epic, obj.object_uuid)

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

    def get_has_endorsed_profile(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        if request is None:
            return None
        return obj.get_has_endorsed_profile(request.user.username)

    def get_has_endorsed_quest(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        if request is None:
            return None
        return obj.get_has_endorsed_quest(request.user.username)

    def get_title_summary(self, obj):
        if obj.title is not None:
            if len(obj.title) > 20:
                return smart_truncate(obj.title, 20)
        return obj.title

    def get_level_readable(self, obj):
        return obj.level.replace('_', ' ')
