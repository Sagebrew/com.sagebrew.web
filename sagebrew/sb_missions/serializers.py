import pytz
from datetime import datetime

from django.core.cache import cache
from django.utils.text import slugify
from django.conf import settings
from django.templatetags.static import static
from django.template.loader import render_to_string

from rest_framework import serializers, status
from rest_framework.reverse import reverse

from neomodel import db, DoesNotExist

from api.utils import (gather_request_data, clean_url, empty_text_to_none,
                       smart_truncate, render_content)
from api.serializers import SBSerializer

from sb_base.serializers import (IntercomEventSerializer,
                                 IntercomMessageSerializer)
from sb_locations.serializers import LocationSerializer
from sb_tags.neo_models import Tag

from .neo_models import Mission
from .utils import setup_onboarding


class MissionSerializer(SBSerializer):
    active = serializers.BooleanField(required=False)
    submitted_for_review = serializers.BooleanField(required=False)
    saved_for_later = serializers.BooleanField(required=False)
    has_feedback = serializers.BooleanField(required=False)
    review_feedback = serializers.MultipleChoiceField(
        required=False, choices=settings.REVIEW_FEEDBACK_OPTIONS)
    completed = serializers.BooleanField(required=False)
    about = serializers.CharField(required=False, allow_blank=True,
                                  max_length=255)
    epic = serializers.CharField(required=False, allow_blank=True)
    temp_epic = serializers.CharField(required=False, allow_blank=True)
    epic_last_autosaved = serializers.DateTimeField(required=False)
    focus_on_type = serializers.ChoiceField(required=True, choices=[
        ('position', "Public Office"), ('advocacy', "Advocacy"),
        ('question', "Question")])
    facebook = serializers.URLField(required=False, allow_blank=True)
    linkedin = serializers.URLField(required=False, allow_blank=True)
    youtube = serializers.URLField(required=False, allow_blank=True)
    twitter = serializers.URLField(required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True)
    wallpaper_pic = serializers.CharField(required=False)
    title = serializers.CharField(max_length=70, required=False,
                                  allow_blank=True)
    owner_username = serializers.CharField(read_only=True)
    location_name = serializers.CharField(required=False, allow_null=True)
    focus_name = serializers.CharField(max_length=70)
    focus_formal_name = serializers.CharField(read_only=True)
    reset_epic = serializers.BooleanField(required=False)

    url = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()
    focused_on = serializers.SerializerMethodField()
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
        setup_onboarding(quest, mission)
        return mission

    def update(self, instance, validated_data):
        from sb_base.serializers import validate_is_owner
        validate_is_owner(self.context.get('request', None), instance)
        instance.completed = validated_data.pop(
            'completed', instance.completed)

        initial_review_state = instance.submitted_for_review
        instance.submitted_for_review = validated_data.pop(
            'submitted_for_review', instance.submitted_for_review)
        instance.saved_for_later = validated_data.get('saved_for_later',
                                                      instance.saved_for_later)
        if instance.submitted_for_review and not initial_review_state and not \
                instance.saved_for_later:
            serializer = IntercomEventSerializer(
                data={'event_name': "submit-mission-for-review",
                      'username': instance.owner_username})
            if serializer.is_valid():
                serializer.save()
            message_data = {
                'message_type': 'email',
                'subject': 'Submit Mission For Review',
                'body': 'Hi Team,\n%s has submitted their %s Mission. '
                        'Please review it in the <a href="%s">'
                        'council area</a>. '
                        % (instance.owner_username, instance.title,
                           reverse('council_missions',
                                   request=self.context.get('request'))),
                'template': "personal",
                'from_user': {
                    'type': "admin",
                    'id': settings.INTERCOM_ADMIN_ID_DEVON},
                'to_user': {
                    'type': "user",
                    'user_id': settings.INTERCOM_USER_ID_DEVON}
            }
            serializer = IntercomMessageSerializer(data=message_data)
            if serializer.is_valid():
                serializer.save()
            db.cypher_query(
                'MATCH (mission:Mission {object_uuid: "%s"})-'
                '[:MUST_COMPLETE]->(task:OnboardingTask {title: "%s"}) '
                'SET task.completed=true RETURN task' % (
                    instance.object_uuid, settings.SUBMIT_FOR_REVIEW))
        title = validated_data.pop('title', instance.title)
        if instance.submitted_for_review and instance.review_feedback \
                and validated_data.get('epic', '') and not instance.active:
            message_data = {
                'message_type': 'email',
                'subject': 'Problem Mission Updated',
                'body': render_to_string(
                    "email_templates/problem_mission_updates.html",
                    context={"username": instance.owner_username,
                             "council_url":
                                 reverse('council_missions',
                                         request=self.context.get('request')),
                             "title": instance.title},
                    request=self.context.get('request')),
                'template': "personal",
                'from_user': {
                    'type': "admin",
                    'id': settings.INTERCOM_ADMIN_ID_DEVON},
                'to_user': {
                    'type': "user",
                    'user_id': settings.INTERCOM_USER_ID_DEVON}
            }
            serializer = IntercomMessageSerializer(data=message_data)
            if serializer.is_valid():
                serializer.save()
        if empty_text_to_none(title) is not None:
            instance.title = title
        instance.about = empty_text_to_none(
            validated_data.get('about', instance.about))
        if instance.about is not None:
            db.cypher_query(
                'MATCH (mission:Mission {object_uuid: "%s"})-'
                '[:MUST_COMPLETE]->(task:OnboardingTask {title: "%s"}) '
                'SET task.completed=true RETURN task' % (
                    instance.object_uuid, settings.MISSION_ABOUT_TITLE))
        instance.epic = validated_data.pop('epic', instance.epic)
        # We expect the epic to be set to None and not "" so that None
        # can be used in this function for checks and the templates.
        instance.epic = empty_text_to_none(render_content(instance.epic))
        prev_temp_epic = instance.temp_epic
        instance.temp_epic = validated_data.pop('temp_epic', instance.temp_epic)
        instance.temp_epic = empty_text_to_none(
            render_content(instance.temp_epic))
        if prev_temp_epic != instance.temp_epic:
            instance.epic_last_autosaved = datetime.now(pytz.utc)
        if instance.epic is not None:
            db.cypher_query(
                'MATCH (mission:Mission {object_uuid: "%s"})-'
                '[:MUST_COMPLETE]->(task:OnboardingTask {title: "%s"}) '
                'SET task.completed=true RETURN task' % (
                    instance.object_uuid, settings.EPIC_TITLE))
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
        if settings.DEFAULT_WALLPAPER not in instance.wallpaper_pic:
            db.cypher_query(
                'MATCH (mission:Mission {object_uuid: "%s"})-'
                '[:MUST_COMPLETE]->(task:OnboardingTask {title: "%s"}) '
                'SET task.completed=true RETURN task' % (
                    instance.object_uuid, settings.MISSION_WALLPAPER_TITLE))
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
        if obj.level is not None:
            return obj.level.replace('_', ' ')
        else:
            return "unknown"


class MissionReviewSerializer(MissionSerializer):
    """
    Using this serializer in place of the traditional MissionSerializer due
    to the operations being performed on the Mission being restricted to our
    admins (us) currently. In the MissionSerializer we have a check for
    verifying the person modifying the Mission is actually the owner.
    I think it is cleaner to have a different serializer for this purpose
    rather than adding in a check there to determine if it is the owner of
    the Mission or us modifying it.
    """
    review_feedback = serializers.ListField(required=False)

    def validate(self, validated_data):
        request = self.context.get('request', '')
        if not request:
            raise serializers.ValidationError(
                "You are not authorized to access this.")
        if request.user.username != 'tyler_wiersing' \
                and request.user.username != 'devon_bleibtrey':
            raise serializers.ValidationError(
                "You are not authorized to access this.")
        return validated_data

    def update(self, instance, validated_data):
        from plebs.neo_models import Pleb
        owner = Pleb.get(instance.owner_username)
        prev_feedback = instance.review_feedback
        instance.review_feedback = validated_data.pop('review_feedback',
                                                      instance.review_feedback)
        if prev_feedback != instance.review_feedback and not instance.active:
            problem_list = [dict(settings.REVIEW_FEEDBACK_OPTIONS)[item]
                            for item in instance.review_feedback]
            message_subject = "Mission Review: Completed"
            message_body = render_to_string(
                'email_templates/mission_review_success.html',
                context={"first_name": owner.first_name,
                         "title": instance.get_mission_title(),
                         "conversation_url":
                             reverse('question-create',
                                     request=self.context.get('request')),
                         "update_url": reverse(
                             'mission_update_create',
                             kwargs={
                                 'object_uuid': instance.object_uuid,
                                 'slug': slugify(instance.get_mission_title())
                             }, request=self.context.get('request')
                         )})
            if problem_list:
                message_subject = "Mission Review: Action Needed"
                message_body = render_to_string(
                    'email_templates/mission_review_errors.html',
                    context=dict(
                        first_name=owner.first_name,
                        title=instance.get_mission_title(),
                        problems=problem_list,
                        epic_link=reverse(
                            'mission_edit_epic',
                            kwargs={
                                'object_uuid': instance.object_uuid,
                                "slug": slugify(instance.get_mission_title())
                            }, request=self.context.get('request'))))
            else:
                instance.active = True

            message_data = {
                'message_type': 'email',
                'subject': message_subject,
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
        cache.delete("%s_mission" % instance.object_uuid)
        return instance.save()
