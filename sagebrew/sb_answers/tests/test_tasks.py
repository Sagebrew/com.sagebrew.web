import pytz
import time
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User

from sb_answers.neo_models import SBAnswer
from sb_answers.utils import save_answer_util
from sb_answers.tasks import save_answer_task, edit_answer_task, vote_answer_task
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

class TestEditAnswerTask(TestCase):
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

    def test_edit_answer_task(self):
        save_q_response = create_question_util(**self.question_info_dict)
        self.answer_info_dict['question_uuid'] = save_q_response.question_id
        self.answer_info_dict.pop('to_pleb', None)
        self.answer_info_dict['answer_uuid'] = str(uuid1())
        save_ans_response = save_answer_util(**self.answer_info_dict)
        edit_dict = {'content': "this is a test edit",
                     'current_pleb': self.pleb.email,
                     'last_edited_on': datetime.now(pytz.utc),
                     'answer_uuid': save_ans_response.answer_id}

        edit_response = edit_answer_task.apply_async(kwargs=edit_dict)

        self.assertTrue(edit_response.get())

    def test_edit_answer_task_missing_data(self):
        save_q_response = create_question_util(**self.question_info_dict)
        self.answer_info_dict['question_uuid'] = save_q_response.question_id
        self.answer_info_dict.pop('to_pleb', None)
        self.answer_info_dict['answer_uuid'] = str(uuid1())
        save_ans_response = save_answer_util(**self.answer_info_dict)
        edit_dict = {'content': "this is a test edit",
                     'current_pleb': self.pleb.email,
                     'last_edited_on': datetime.now(pytz.utc)}

        edit_response = edit_answer_task.apply_async(kwargs=edit_dict)

        self.assertFalse(edit_response.get())

class TestVoteAnswerTask(TestCase):
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

    def test_vote_answer_task(self):
        answer = SBAnswer(answer_id=str(uuid1()), content="test answer")
        answer.save()
        my_dict = {'vote_type': 'up', 'current_pleb': self.pleb.email,
                   'answer_uuid': answer.answer_id}
        response = vote_answer_task.apply_async(kwargs=my_dict)

        self.assertTrue(response.get())

    def test_vote_answer_task_missing_data(self):
        answer = SBAnswer(answer_id=str(uuid1()), content="test answer")
        answer.save()
        my_dict = {'vote_type': 'up', 'current_pleb': self.pleb.email,
                   'answer_uuid': ''}
        response = vote_answer_task.apply_async(kwargs=my_dict)
        time.sleep(1)
        self.assertFalse(response.get())