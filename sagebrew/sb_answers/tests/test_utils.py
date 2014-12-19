from uuid import uuid1
from django.test import TestCase
from sb_answers.utils import save_answer_util


class TestCreateAnswerUtil(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.answer_info_dict = {'content': 'test answer',
                                 'answer_uuid': str(uuid1()),}

    def test_save_answer_util(self):
        response = save_answer_util(**self.answer_info_dict)
        self.assertTrue(response)

    def test_save_existing_answer(self):
        save_answer_util(**self.answer_info_dict)
        response2 = save_answer_util(**self.answer_info_dict)
        self.assertTrue(response2)


