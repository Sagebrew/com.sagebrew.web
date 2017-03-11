from django.utils.text import slugify
from django.core.cache import cache
from rest_framework.reverse import reverse

from neomodel import (db, StringProperty, IntegerProperty)

from sagebrew.sb_base.neo_models import SBPublicContent


class Solution(SBPublicContent):
    table = StringProperty(default='public_solutions')
    action_name = StringProperty(default="offered a solution to your question")
    parent_id = StringProperty()
    visibility = StringProperty(default="public")
    up_vote_adjustment = IntegerProperty(default=10)
    down_vote_adjustment = IntegerProperty(default=-10)
    down_vote_cost = IntegerProperty(default=-2)

    def get_url(self, request=None):
        from sagebrew.sb_questions.neo_models import Question
        question = Question.get(object_uuid=self.parent_id)
        return reverse('question_detail_page',
                       kwargs={'question_uuid': self.parent_id,
                               'slug': slugify(question.title)},
                       request=request)

    @classmethod
    def get_mission(cls, object_uuid, request=None):
        from sagebrew.sb_missions.neo_models import Mission
        from sagebrew.sb_missions.serializers import MissionSerializer
        mission = cache.get("%s_mission" % object_uuid)
        if mission is None:
            query = 'MATCH (solution:Solution {object_uuid:"%s"})<-' \
                    '[:POSSIBLE_ANSWER]-(question:Question)' \
                    '<-[:ASSOCIATED_WITH]-' \
                    '(mission:Mission) RETURN mission' % object_uuid
            res, _ = db.cypher_query(query)
            if res.one:
                mission = MissionSerializer(
                    Mission.inflate(res.one), context={"request": request}).data
                cache.set("%s_mission" % object_uuid, mission)
        return mission
