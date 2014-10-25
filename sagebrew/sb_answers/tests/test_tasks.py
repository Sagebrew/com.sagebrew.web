import pytz
import time
from uuid import uuid1
from datetime import datetime
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import test_wait_util
from sb_answers.neo_models import SBAnswer
from sb_answers.utils import save_answer_util
from sb_answers.tasks import save_answer_task, edit_answer_task, vote_answer_task
from sb_questions.neo_models import SBQuestion
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util

class TestSaveAnswerTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post',}
        self.answer_info_dict = {'current_pleb': self.user.email,
                                 'content': 'test answer',
                                 'to_pleb': self.user.email}
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False


    def test_save_answer_task(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        self.answer_info_dict['question_uuid'] = question.question_id
        save_response = save_answer_task.apply_async(kwargs=self.answer_info_dict)

        while not save_response.ready():
            time.sleep(1)
        save_response = save_response.result

        self.assertIsNotNone(question)
        self.assertTrue(save_response)

    def test_save_answer_task_fail(self):
        question_response = SBQuestion(question_id=str(uuid1()))
        question_response.save()
        save_response = save_answer_task.apply_async(kwargs=self.answer_info_dict)

        while not save_response.ready():
            time.sleep(1)
        save_response = save_response.result

        self.assertEqual(type(save_response), TypeError)

class TestEditAnswerTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post',}
        self.answer_info_dict = {'current_pleb': self.user.email,
                                 'content': 'test answer',
                                 'to_pleb': self.user.email}
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_edit_answer_task(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        question.owned_by.connect(self.pleb)
        self.answer_info_dict['question_uuid'] = question.question_id
        self.answer_info_dict.pop('to_pleb', None)
        self.answer_info_dict['answer_uuid'] = str(uuid1())
        save_ans_response = save_answer_util(**self.answer_info_dict)
        edit_dict = {'content': "this is a test edit",
                     'current_pleb': self.user.email,
                     'last_edited_on': datetime.now(pytz.utc),
                     'answer_uuid': save_ans_response.answer_id}

        edit_response = edit_answer_task.apply_async(kwargs=edit_dict)
        while not edit_response.ready():
            time.sleep(1)
        edit_response = edit_response.result

        self.assertTrue(edit_response)

    def test_edit_answer_task_missing_data(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        question.owned_by.connect(self.pleb)
        self.answer_info_dict['question_uuid'] = question.question_id
        self.answer_info_dict.pop('to_pleb', None)
        self.answer_info_dict['answer_uuid'] = str(uuid1())
        save_ans_response = save_answer_util(**self.answer_info_dict)
        edit_dict = {'content': "this is a test edit",
                     'current_pleb': self.user.email,
                     'last_edited_on': datetime.now(pytz.utc)}

        edit_response = edit_answer_task.apply_async(kwargs=edit_dict)
        while not edit_response.ready():
            time.sleep(1)
        edit_response = edit_response.result

        self.assertFalse(edit_response)

    def test_edit_answer_task_failure_pleb_does_not_exist(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        question.owned_by.connect(self.pleb)
        self.answer_info_dict['question_uuid'] = question.question_id
        self.answer_info_dict.pop('to_pleb', None)
        self.answer_info_dict['answer_uuid'] = str(uuid1())
        save_ans_response = save_answer_util(**self.answer_info_dict)
        edit_dict = {'content': "this is a test edit",
                     'current_pleb': str(uuid1()),
                     'last_edited_on': datetime.now(pytz.utc),
                     'answer_uuid': save_ans_response.answer_id}

        edit_response = edit_answer_task.apply_async(kwargs=edit_dict)
        while not edit_response.ready():
            time.sleep(1)
        edit_response = edit_response.result

        self.assertFalse(edit_response)

    def test_edit_answer_task_failure_to_be_deleted(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        question.owned_by.connect(self.pleb)
        self.answer_info_dict['question_uuid'] = question.question_id
        self.answer_info_dict.pop('to_pleb', None)
        self.answer_info_dict['answer_uuid'] = str(uuid1())
        save_ans_response = save_answer_util(**self.answer_info_dict)
        save_ans_response.to_be_deleted = True
        save_ans_response.save()
        edit_dict = {'content': "this is a test edit",
                     'current_pleb': self.user.email,
                     'last_edited_on': datetime.now(pytz.utc),
                     'answer_uuid': save_ans_response.answer_id}

        edit_response = edit_answer_task.apply_async(kwargs=edit_dict)
        while not edit_response.ready():
            time.sleep(1)
        edit_response = edit_response.result

        self.assertFalse(edit_response)

    def test_edit_answer_task_failure_same_content(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        question.owned_by.connect(self.pleb)
        self.answer_info_dict['question_uuid'] = question.question_id
        self.answer_info_dict.pop('to_pleb', None)
        self.answer_info_dict['answer_uuid'] = str(uuid1())
        save_ans_response = save_answer_util(**self.answer_info_dict)
        edit_dict = {'content': self.answer_info_dict['content'],
                     'current_pleb': self.user.email,
                     'last_edited_on': datetime.now(pytz.utc),
                     'answer_uuid': save_ans_response.answer_id}

        edit_response = edit_answer_task.apply_async(kwargs=edit_dict)
        while not edit_response.ready():
            time.sleep(1)
        edit_response = edit_response.result

        self.assertFalse(edit_response)

    def test_edit_answer_task_failure_same_timestamp(self):
        now = datetime.now(pytz.utc)
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        question.owned_by.connect(self.pleb)
        self.answer_info_dict['question_uuid'] = question.question_id
        self.answer_info_dict.pop('to_pleb', None)
        self.answer_info_dict['answer_uuid'] = str(uuid1())
        save_ans_response = save_answer_util(**self.answer_info_dict)
        save_ans_response.last_edited_on = now
        save_ans_response.save()
        edit_dict = {'content': "this is a test edit",
                     'current_pleb': self.user.email,
                     'last_edited_on': now,
                     'answer_uuid': save_ans_response.answer_id}

        edit_response = edit_answer_task.apply_async(kwargs=edit_dict)
        while not edit_response.ready():
            time.sleep(1)
        edit_response = edit_response.result

        self.assertFalse(edit_response)

    def test_edit_answer_task_failure_last_edit_more_recent(self):
        now = datetime.now(pytz.utc)
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        question.owned_by.connect(self.pleb)
        self.answer_info_dict['question_uuid'] = question.question_id
        self.answer_info_dict.pop('to_pleb', None)
        self.answer_info_dict['answer_uuid'] = str(uuid1())
        save_ans_response = save_answer_util(**self.answer_info_dict)
        save_ans_response.last_edited_on = datetime.now(pytz.utc)
        save_ans_response.save()
        edit_dict = {'content': "this is a test edit",
                     'current_pleb': self.user.email,
                     'last_edited_on': now,
                     'answer_uuid': save_ans_response.answer_id}

        edit_response = edit_answer_task.apply_async(kwargs=edit_dict)
        while not edit_response.ready():
            time.sleep(1)
        edit_response = edit_response.result

        self.assertFalse(edit_response)


class TestVoteAnswerTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post',}
        self.answer_info_dict = {'current_pleb': self.user.email,
                                 'content': 'test answer',
                                 'to_pleb': self.user.email}
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_vote_answer_task_success_up(self):
        answer = SBAnswer(answer_id=str(uuid1()), content="test answer")
        answer.save()
        my_dict = {'vote_type': 'up', 'current_pleb': self.user.email,
                   'answer_uuid': answer.answer_id}
        response = vote_answer_task.apply_async(kwargs=my_dict)
        while not response.ready():
            time.sleep(3)
        self.assertTrue(response.result)

    def test_vote_answer_task_success_down(self):
        answer = SBAnswer(answer_id=str(uuid1()), content="test answer")
        answer.save()
        my_dict = {'vote_type': 'down', 'current_pleb': self.user.email,
                   'answer_uuid': answer.answer_id}
        response = vote_answer_task.apply_async(kwargs=my_dict)
        while not response.ready():
            time.sleep(3)
        self.assertTrue(response.result)

    def test_vote_answer_task_missing_data(self):
        answer = SBAnswer(answer_id=str(uuid1()), content="test answer")
        answer.save()
        my_dict = {'vote_type': 'up', 'current_pleb': self.user.email,
                   'answer_uuid': ''}
        response = vote_answer_task.apply_async(kwargs=my_dict)
        while not response.ready():
            time.sleep(3)
        self.assertFalse(response.result)

    def test_vote_answer_task_failure_pleb_does_not_exist(self):
        answer = SBAnswer(answer_id=str(uuid1()), content="test answer")
        answer.save()
        my_dict = {'vote_type': 'up', 'current_pleb': str(uuid1()),
                   'answer_uuid': answer.answer_id}
        response = vote_answer_task.apply_async(kwargs=my_dict)
        while not response.ready():
            time.sleep(3)
        self.assertFalse(response.result)

    def test_vote_answer_task_failure_pleb_already_voted(self):
        answer = SBAnswer(answer_id=str(uuid1()), content="test answer")
        answer.save()
        answer.up_voted_by.connect(self.pleb)
        my_dict = {'vote_type': 'up', 'current_pleb': self.user.email,
                   'answer_uuid': answer.answer_id}
        response = vote_answer_task.apply_async(kwargs=my_dict)
        while not response.ready():
            time.sleep(3)
        self.assertFalse(response.result)