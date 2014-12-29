from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util
from sb_questions.neo_models import SBQuestion


class TestSBQuestionNeoModel(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = SBQuestion(content='test content',
                                   sb_id=str(uuid1())).save()
        self.question.owned_by.connect(self.pleb)

    def test_get_multiple_question_dict(self):
        res = self.question.get_multiple_question_dict(self.pleb)

        self.assertIsInstance(res, dict)

    def test_add_tags(self):
        res = self.question.add_tags('thisisatesttag1,thisisatesttag2')

        self.assertTrue(res)

    def test_add_auto_tags(self):
        auto_tags = [{'tags': {'text': 'testautotag', 'relevance': 0.10201}}]
        res = self.question.add_auto_tags(auto_tags)

        self.assertIsInstance(res, list)

    def test_get_original(self):
        self.assertIsInstance(self.question.get_original(), SBQuestion)

    def test_get_original_edit_to(self):
        question = SBQuestion(content="test", sb_id=str(uuid1()),
                              original=False).save()

        question.edit_to.connect(self.question)

        self.assertEqual(question.get_original(), self.question)