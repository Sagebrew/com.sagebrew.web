from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User
from neomodel.exception import DoesNotExist

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_answers.utils import save_answer_util
from sb_questions.neo_models import SBQuestion
from sb_registration.utils import create_user_util

class TestCreateAnswerUtil(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post'}
        self.answer_info_dict = {'question_uuid': '',
                                 'content': 'test answer',
                                 'answer_uuid': str(uuid1()),
                                 'current_pleb': self.user.email}


    def test_save_answer_util(self):
        self.question_info_dict['sb_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        self.answer_info_dict['question_uuid'] = question.sb_id
        response = save_answer_util(**self.answer_info_dict)

        self.assertIsNot(response, False)

    def test_save_answer_util_question_does_not_exist(self):
        self.answer_info_dict['question_uuid'] = '246646156156615'
        response = save_answer_util(**self.answer_info_dict)

        self.assertIsInstance(response, DoesNotExist)

    def test_save_answer_util_pleb_does_not_exist(self):
        self.question_info_dict['sb_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        self.answer_info_dict['question_uuid'] = question.sb_id
        response = save_answer_util(**self.answer_info_dict)

        self.assertFalse(response)


