from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_answers.neo_models import SBAnswer
from sb_questions.neo_models import SBQuestion


class TestSBAnswerNeoModel(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.answer = SBAnswer(content="test answer content",
                               sb_id=str(uuid1())).save()
        self.question = SBQuestion(content='test question content',
                                   sb_id=str(uuid1())).save()

    def test_edit_content(self):
        self.assertFalse(isinstance(self.answer.edit_content('test edit',
                                                             self.pleb),
                                    Exception))

    def test_create_relations(self):
        self.assertTrue(self.answer.create_relations(self.pleb, self.question))

    def test_create_relations_no_question(self):
        self.assertFalse(self.answer.create_relations(self.pleb))
        