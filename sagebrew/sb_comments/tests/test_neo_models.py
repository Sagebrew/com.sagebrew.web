from uuid import uuid1

from django.contrib.auth.models import User
from django.test import TestCase
from django.core.cache import cache

from sb_posts.neo_models import Post
from sb_questions.neo_models import Question
from sb_solutions.neo_models import Solution
from sb_comments.neo_models import Comment
from sb_registration.utils import create_user_util_test
from sb_missions.neo_models import Mission
from sb_quests.neo_models import Quest


class TestCommentsNeoModels(TestCase):

    def setUp(self):
        self.unit_under_test_name = 'comment'
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.comment = Comment(content="test comment",
                               owner_username=self.pleb.username).save()
        self.comment.owned_by.connect(self.pleb)

    def test_get_mission_solution(self):
        solution = Solution(content='test content').save()
        solution.comments.connect(self.comment)
        quest = Quest(owner_username=self.pleb.username).save()
        quest.owner.connect(self.pleb)
        mission = Mission(owner_username=self.pleb.username).save()
        quest.missions.connect(mission)
        question = Question(content='test content title',
                            title=str(uuid1())).save()
        question.solutions.connect(solution)
        mission.associated_with.connect(question)
        self.comment.parent_type = "solution"
        self.comment.parent_id = solution.object_uuid
        self.comment.save()
        cache.clear()
        res = self.comment.get_mission(self.comment.object_uuid, None)
        self.assertEqual(res['id'], mission.object_uuid)
        mission.delete()
        quest.delete()

    def test_get_mission_question(self):
        quest = Quest(owner_username=self.pleb.username).save()
        quest.owner.connect(self.pleb)
        mission = Mission(owner_username=self.pleb.username).save()
        quest.missions.connect(mission)
        question = Question(content='test content title',
                            title=str(uuid1())).save()
        mission.associated_with.connect(question)
        question.comments.connect(self.comment)
        self.comment.parent_type = "question"
        self.comment.parent_id = question.object_uuid
        self.comment.save()
        cache.clear()
        res = self.comment.get_mission(self.comment.object_uuid, None)
        self.assertEqual(res['id'], mission.object_uuid)
        mission.delete()
        quest.delete()

    def test_get_mission_post(self):
        post = Post(content='test content').save()
        post.comments.connect(self.comment)
        self.comment.parent_type = "post"
        self.comment.parent_id = post.object_uuid
        self.comment.save()
        res = self.comment.get_mission(self.comment.object_uuid, None)
        self.assertIsNone(res)
