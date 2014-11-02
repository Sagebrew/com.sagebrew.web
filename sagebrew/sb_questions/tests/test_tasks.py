import pytz
import time
from uuid import uuid1
from datetime import datetime
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from neomodel.exception import DoesNotExist

from api.utils import test_wait_util
from sb_questions.tasks import (create_question_task, edit_question_task)
from plebs.neo_models import Pleb
from sb_questions.neo_models import SBQuestion
from sb_registration.utils import create_user_util


class TestSaveQuestionTask(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post',
                                   'tags': "this,is,a,test"}

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_save_question_task(self):
        response = create_question_task.apply_async(
            kwargs=self.question_info_dict)
        while not response.ready():
            time.sleep(1)

        self.assertTrue(response.result)

    def test_save_question_task_fail(self):
        question_info = {'current_pleb': self.user.email,
                         'question_title': "Test question",
                         'tags': "this,is,a,test"}
        response = create_question_task.apply_async(kwargs=question_info)

        while not response.ready():
            time.sleep(3)

        result = response.result
        self.assertTrue(isinstance(result, Exception))

    def test_save_question_task_question_exists(self):
        question = SBQuestion(sb_id=str(uuid1()))
        question.save()

        self.question_info_dict['question_uuid'] = question.sb_id

        res = create_question_task.apply_async(kwargs=self.question_info_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertFalse(res)


class TestEditQuestionTask(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post',
                                   'question_uuid': str(uuid1())}

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_edit_question_task(self):
        question = SBQuestion(content="test question from edit task test",
                              question_title="testquestiontitle from edit test",
                              sb_id=uuid1())
        question.save()
        edit_question_dict = {'content': 'question edited',
                          'question_uuid': question.sb_id,
                          'current_pleb': self.user.email,
                          'last_edited_on': datetime.now(pytz.utc)}
        edit_response = edit_question_task.apply_async(
            kwargs=edit_question_dict)
        while not edit_response.ready():
            time.sleep(1)
        edit_response = edit_response.result
        self.assertTrue(edit_response)

    def test_edit_question_task_failure_pleb_does_not_exist(self):
        question = SBQuestion(sb_id=str(uuid1()))
        question.save()

        task_data = {
            'content': 'edit',
            'question_uuid': question.sb_id,
            'current_pleb': str(uuid1())
        }

        res = edit_question_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertFalse(res)

    def test_edit_question_task_failure_question_does_not_exist(self):
        task_data = {
            'content': 'edit',
            'question_uuid': str(uuid1()),
            'current_pleb': self.user.email
        }

        res = edit_question_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(isinstance(res, DoesNotExist))

    def test_edit_question_task_failure_to_be_deleted(self):
        question = SBQuestion(sb_id=str(uuid1()))
        question.to_be_deleted = True
        question.save()

        task_data = {
            'content': 'edit',
            'question_uuid': question.sb_id,
            'current_pleb': self.user.email
        }

        res = edit_question_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertFalse(res)

    def test_edit_question_task_failure_same_content(self):
        question = SBQuestion(sb_id=str(uuid1()), content='edit')
        question.save()

        task_data = {
            'content': 'edit',
            'question_uuid': question.sb_id,
            'current_pleb': self.user.email
        }

        res = edit_question_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertFalse(res)

    def test_edit_question_task_failure_same_timestamp(self):
        now = datetime.now(pytz.utc)
        question = SBQuestion(sb_id=str(uuid1()), content='edit')
        question.last_edited_on = now
        question.save()

        task_data = {
            'content': 'edit',
            'question_uuid': question.sb_id,
            'current_pleb': self.user.email,
            'last_edited_on': now
        }

        res = edit_question_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertFalse(res)

    def test_edit_question_task_failure_more_recent_edit(self):
        now = datetime.now(pytz.utc)
        question = SBQuestion(sb_id=str(uuid1()), content='edit')
        question.last_edited_on = datetime.now(pytz.utc)
        question.save()

        task_data = {
            'content': 'edit',
            'question_uuid': question.sb_id,
            'current_pleb': self.user.email,
            'last_edited_on': now
        }

        res = edit_question_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertFalse(res)


class TestQuestionTaskRaceConditions(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'current_pleb': self.pleb.email,
                                   'question_title': "Test question",
                                   'content': 'test post',
                                   'question_uuid': str(uuid1())}

    def test_race_condition_edit_multiple_times(self):
        edit_array = []
        question = SBQuestion(**self.question_info_dict)
        question.save()

        edit_dict = {'content': "post edited",
                     'question_uuid': question.sb_id,
                     'current_pleb': self.user.email,
                     'last_edited_on': datetime.now(pytz.utc)}
        for num in range(1, 10):
            edit_dict['content'] = "post edited" + str(uuid1())
            edit_dict['last_edited_on'] = datetime.now(pytz.utc)
            edit_response = edit_question_task.apply_async(kwargs=edit_dict)
            while not edit_response.ready():
                time.sleep(3)
            edit_response = edit_response.result
            edit_array.append(edit_response)

        self.assertNotIn(False, edit_array)


class TestMultipleTasks(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'current_pleb': self.pleb.email,
                                   'question_title': "Test question",
                                   'content': 'test post',
                                   'question_uuid': str(uuid1())}

    def test_create_many_questions(self):
        response_array = []
        for num in range(1, 10):
            uuid = str(uuid1())
            self.question_info_dict['question_uuid'] = uuid
            save_response = create_question_task.apply_async(
                kwargs=self.question_info_dict)
            while not save_response.ready():
                time.sleep(1)
            response_array.append(save_response.result)

        self.assertNotIn(False, response_array)

    def test_create_same_question_twice(self):
        question = SBQuestion(content="test question", question_title="title",
                              sb_id=str(uuid1()))
        question.save()
        post_info_dict = {'current_pleb': self.pleb.email,
                          'question_title': 'Question Title',
                          'content': 'test question',
                          'question_uuid': question.sb_id}
        response2 = create_question_task.apply_async(kwargs=post_info_dict)
        while not response2.ready():
            time.sleep(1)
        response2 = response2.result
        self.assertFalse(response2)
