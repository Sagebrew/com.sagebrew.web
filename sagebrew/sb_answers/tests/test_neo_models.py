from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util
from sb_answers.neo_models import SBAnswer


class TestSBAnswerNeoModel(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.answer = SBAnswer(content="test answer content",
                               sb_id=str(uuid1())).save()

    def test_edit_content(self):
        self.assertFalse(isinstance(self.answer.edit_content('test edit',
                                                             self.pleb),
                                    Exception))