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
    title = serializers.CharField(required=False,
                                  min_length=5, max_length=140)
    goals = serializers.SerializerMethodField()
    campaign = serializers.SerializerMethodField()

    def create(self, validated_data):
        # TODO we don't have a way currently to distinguish what a Update is
        # about. Think it'll be based on an attribute submitted by the front
        # end. That will be based on where it's at (make update from Public
        # Office Mission vs Advocate Mission vs Quest vs etc)
        request, _, _, _, _ = gather_request_data(self.context)
        quest = validated_data.pop('quest', None)
        associated_goals = validated_data.pop('associated_goals', [])
        validated_data['content'] = bleach.clean(validated_data.get(
            'content', ""))
        owner = Pleb.get(request.user.username)
        validated_data['owner_username'] = owner.username
        update = Update(**validated_data).save()
        quest.updates.connect(update)
        update.owned_by.connect(owner)
        for goal in associated_goals:
            query = 'MATCH (c:Quest {object_uuid:"%s"})-[:EMBARKS_ON]->' \
                    '(mission:Mission)-[:WORKING_TOWARDS]->' \
                    '(g:Goal {title:"%s"}) ' \
                    'RETURN g' % (quest.object_uuid, goal)
            res, _ = db.cypher_query(query)
            goal = Goal.inflate(res.one)
            update.goals.connect(goal)
            goal.updates.connect(update)
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

    def get_campaign(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        campaign = Update.get_campaign(obj.object_uuid)
        if campaign is not None and relation == 'hyperlink':
            return reverse('campaign-detail',
                           kwargs={'object_uuid': campaign},
                           request=request)
        return campaign

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
