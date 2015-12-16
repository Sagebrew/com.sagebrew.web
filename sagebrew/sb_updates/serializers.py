from datetime import datetime
import pytz
import bleach

from django.core.cache import cache

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import db

from plebs.neo_models import Pleb
from sb_goals.neo_models import Goal
from api.utils import gather_request_data
from sb_base.serializers import TitledContentSerializer


from .neo_models import Update


class UpdateSerializer(TitledContentSerializer):
    title = serializers.CharField(min_length=5, max_length=140)
    goals = serializers.SerializerMethodField()
    about_type = serializers.ChoiceField(choices=[
        ('mission', "Mission"), ('quest', "Quest"), ('seat', "Seat"),
        ('goal', "Goal")])
    about_id = serializers.CharField(min_length=36, max_length=36)
    about = serializers.SerializerMethodField()

    def create(self, validated_data):
        # TODO we don't have a way currently to distinguish what a Update is
        # about. Think it'll be based on an attribute submitted by the front
        # end. That will be based on where it's at (make update from Public
        # Office Mission vs Advocate Mission vs Quest vs etc)
        request, _, _, _, _ = gather_request_data(self.context)
        quest = validated_data.pop('quest', None)

        validated_data['content'] = bleach.clean(validated_data.get(
            'content', ""))
        owner = Pleb.get(request.user.username)
        validated_data['owner_username'] = owner.username
        about = validated_data.pop('about', None)
        about_type = validated_data.get('about_type')
        update = Update(**validated_data).save()
        quest.updates.connect(update)
        if validated_data.get('about_type') == "goal":
            query = 'MATCH (c:Quest {object_uuid:"%s"})-[:EMBARKS_ON]->' \
                    '(mission:Mission)-[:WORKING_TOWARDS]->' \
                    '(g:Goal {title:"%s"}) ' \
                    'RETURN g' % (quest.object_uuid,
                                  validated_data.get('about_id'))
            res, _ = db.cypher_query(query)
            goal = Goal.inflate(res.one)
            update.goals.connect(goal)
            goal.updates.connect(update)
        if about_type == 'mission':
            update.mission.connect(about)
        elif about_type == 'quest':
            update.quest.connect(about)
        cache.delete("%s_updates" % quest.object_uuid)
        return update

    def update(self, instance, validated_data):
        instance.title = validated_data.pop('title', instance.title)
        instance.content = validated_data.pop('content', instance.content)
        instance.last_edited_on = datetime.now(pytz.utc)
        instance.save()
        return instance

    def get_goals(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return Update.get_goals(obj.object_uuid)

    def get_url(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return reverse('quest_updates',
                       kwargs={'username': obj.owner_username},
                       request=request)

    def get_href(self, obj):
        request, _, _, _, _ = gather_request_data(
            self.context,
            expedite_param=self.context.get('expedite_param', None),
            expand_param=self.context.get('expand_param', None))
        return reverse(
            'update-detail', kwargs={'object_uuid': obj.object_uuid},
            request=request)

    def get_about(self, obj):
        from sb_missions.neo_models import Mission
        from sb_missions.serializers import MissionSerializer
        from sb_quests.neo_models import Quest
        from sb_quests.serializers import QuestSerializer
        query = 'MATCH (update:Update {object_uuid: "%s"})-[:ABOUT]' \
                '->' % obj.object_uuid
        if obj.about_type == "mission":
            query += '(mission:Mission) RETURN mission'
            res, _ = db.cypher_query(query)
            return MissionSerializer(Mission.inflate(res.one)).data
        elif obj.about_type == "quest":
            query += '(quest:Quest) RETURN quest'
            res, _ = db.cypher_query(query)
            return QuestSerializer(Quest.inflate(res.one)).data
        else:
            return None
