from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from neomodel import db

from plebs.neo_models import Pleb
from sb_tags.neo_models import Tag
from sb_registration.utils import create_user_util_test
from sb_questions.neo_models import Question
from sb_solutions.neo_models import Solution
from sb_missions.neo_models import Mission
from sb_quests.neo_models import Quest


class TestSolutionNeoModels(TestCase):

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(content='test content',
                                 object_uuid=str(uuid1()),
                                 owner_username=self.pleb.username,
                                 title=str(uuid1())).save()
        self.quest = Quest(owner_username=self.pleb.username).save()
        self.mission = Mission(owner_username=self.pleb.username).save()
        self.quest.missions.connect(self.mission)
        self.quest.owner.connect(self.pleb)
        self.mission.associated_with.connect(self.question)
        self.question.owned_by.connect(self.pleb)

    def test_get_mission(self):
        solution = Solution(content='some test content').save()
        self.question.solutions.connect(solution)
        res = Solution.get_mission(solution.object_uuid)
        self.assertEqual(res['id'], self.mission.object_uuid)

