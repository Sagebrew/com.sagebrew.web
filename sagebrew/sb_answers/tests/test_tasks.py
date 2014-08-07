import pytz
import time
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User

from sb_answers.tasks import save_answer_task
from sb_questions.utils import create_question_util
from plebs.neo_models import Pleb

class TestSaveAnswerTask(TestCase):
    def setUp(self):
        self.email = 'devon@sagebrew.com'
        try:
            pleb = Pleb.index.get(email=self.email)
            pleb.delete()
        except Pleb.DoesNotExist:
            pass

        self.user = User.objects.create_user(
            username='Tyler' + str(uuid1())[:25], email=self.email)
        self.pleb = Pleb.index.get(email=self.email)

        self.question_info_dict = {'current_pleb': self.pleb.email,
                                   'question_title': "Test question",
                                   'content': 'test post',}
        self.answer_info_dict = {'current_pleb': self.pleb.email,
                                 'content': 'test answer',
                                 'to_pleb': self.user.email}

    def test_save_answer_task(self):
        question_response = create_question_util(**self.question_info_dict)
        self.answer_info_dict['question_uuid'] = question_response.question_id
        save_response = save_answer_task.apply_async(kwargs=self.answer_info_dict)

        self.assertIsNotNone(question_response)
        self.assertTrue(save_response.get())

    def test_save_answer_task_fail(self):
        question_response = create_question_util(**self.question_info_dict)
        save_response = save_answer_task.apply_async(kwargs=self.answer_info_dict)

        self.assertIsNotNone(question_response)
        self.assertFalse(save_response.get())
