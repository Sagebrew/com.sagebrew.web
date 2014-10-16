import pytz
import time
from uuid import uuid1
from datetime import datetime
from django.conf import settings
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User
from celery.utils.serialization import UnpickleableExceptionWrapper

from sb_questions.tasks import (create_question_task, edit_question_task,
                                vote_question_task)
from plebs.neo_models import Pleb
from sb_questions.neo_models import SBQuestion


class TestSaveQuestionTask(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post',
                                   'tags': "this,is,a,test"}

    def tearDown(self):
        call_command('clear_neo_db')
        settings.CELERY_ALWAYS_EAGER = False

    def test_save_question_task(self):
        response = create_question_task.apply_async(kwargs=self.question_info_dict)
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
        if not result:
            self.assertFalse(response.result)
        elif type(result) is TypeError:
            self.assertTrue(type(result) is TypeError)

    def test_save_question_task_question_exists(self):
        question = SBQuestion(question_id=str(uuid1()))
        question.save()

        self.question_info_dict['question_uuid'] = question.question_id

        res = create_question_task.apply_async(kwargs=self.question_info_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertFalse(res)


class TestEditQuestionTask(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post',
                                   'question_uuid': str(uuid1())}

    def tearDown(self):
        call_command('clear_neo_db')
        settings.CELERY_ALWAYS_EAGER = False


    def test_edit_question_task(self):
        question = SBQuestion(content="test question from edit task test",
                              question_title="testquestiontitle from edit test",
                              question_id=uuid1())
        question.save()
        edit_question_dict = {'content': 'question edited',
                          'question_uuid': question.question_id,
                          'current_pleb': self.user.email,
                          'last_edited_on': datetime.now(pytz.utc)}
        edit_response = edit_question_task.apply_async(kwargs=edit_question_dict)
        while not edit_response.ready():
            time.sleep(1)
        edit_response = edit_response.result
        self.assertTrue(edit_response)

    def test_edit_question_task_failure_pleb_does_not_exist(self):
        question = SBQuestion(question_id=str(uuid1()))
        question.save()

        task_data = {
            'content': 'edit',
            'question_uuid': question.question_id,
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

        self.assertEqual(type(res), UnpickleableExceptionWrapper)

    def test_edit_question_task_failure_to_be_deleted(self):
        question = SBQuestion(question_id=str(uuid1()))
        question.to_be_deleted = True
        question.save()

        task_data = {
            'content': 'edit',
            'question_uuid': question.question_id,
            'current_pleb': self.user.email
        }

        res = edit_question_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertFalse(res)

    def test_edit_question_task_failure_same_content(self):
        question = SBQuestion(question_id=str(uuid1()), content='edit')
        question.save()

        task_data = {
            'content': 'edit',
            'question_uuid': question.question_id,
            'current_pleb': self.user.email
        }

        res = edit_question_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertFalse(res)

    def test_edit_question_task_failure_same_timestamp(self):
        now = datetime.now(pytz.utc)
        question = SBQuestion(question_id=str(uuid1()), content='edit')
        question.last_edited_on = now
        question.save()

        task_data = {
            'content': 'edit',
            'question_uuid': question.question_id,
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
        question = SBQuestion(question_id=str(uuid1()), content='edit')
        question.last_edited_on = datetime.now(pytz.utc)
        question.save()

        task_data = {
            'content': 'edit',
            'question_uuid': question.question_id,
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
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        self.question_info_dict = {'current_pleb': self.pleb.email,
                                   'question_title': "Test question",
                                   'content': 'test post',
                                   'question_uuid': str(uuid1())}

    def tearDown(self):
        call_command('clear_neo_db')

    def test_race_condition_edit_multiple_times(self):
        print settings.CELERY_ALWAYS_EAGER
        if settings.CELERY_ALWAYS_EAGER:
            settings.CELERY_ALWAYS_EAGER = False
        edit_array = []
        question = SBQuestion(**self.question_info_dict)
        question.save()

        edit_dict = {'content': "post edited",
                     'question_uuid': question.question_id,
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

class TestVoteTask(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post',
                                   'question_uuid': str(uuid1())}
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        call_command('clear_neo_db')
        settings.CELERY_ALWAYS_EAGER = False

    def test_question_vote_task_up_success(self):
        question = SBQuestion(content="test question from vote task test",
                              question_title="testquestiontitle from votetest",
                              question_id=uuid1())
        question.save()
        pleb = Pleb.nodes.get(email=self.user.email)
        vote_info_dict = {"question_uuid": question.question_id,
                          "current_pleb": pleb.email, 'vote_type': 'up'}
        vote_response = vote_question_task.apply_async(kwargs=vote_info_dict)
        while not vote_response.ready():
            time.sleep(1)
        vote_response = vote_response.result
        self.assertTrue(vote_response)

    def test_question_vote_task_down_success(self):
        question = SBQuestion(content="test question from vote task test",
                              question_title="testquestiontitle from votetest",
                              question_id=uuid1())
        question.save()
        pleb = Pleb.nodes.get(email=self.user.email)
        vote_info_dict = {"question_uuid": question.question_id,
                          "current_pleb": pleb.email, 'vote_type': 'down'}
        vote_response = vote_question_task.apply_async(kwargs=vote_info_dict)
        while not vote_response.ready():
            time.sleep(1)
        vote_response = vote_response.result
        self.assertTrue(vote_response)

    def test_question_vote_task_pleb_does_not_exist(self):
        question = SBQuestion(content="test question from vote task test",
                              question_title="testquestiontitle from votetest",
                              question_id=uuid1())
        question.save()
        pleb = Pleb.nodes.get(email=self.user.email)
        vote_info_dict = {"question_uuid": question.question_id,
                          "current_pleb": str(uuid1()), 'vote_type': 'up'}
        vote_response = vote_question_task.apply_async(kwargs=vote_info_dict)
        while not vote_response.ready():
            time.sleep(1)
        vote_response = vote_response.result
        self.assertFalse(vote_response)

    def test_question_vote_task_question_does_not_exist(self):
        question = SBQuestion(content="test question from vote task test",
                              question_title="testquestiontitle from votetest",
                              question_id=uuid1())
        question.save()
        pleb = Pleb.nodes.get(email=self.user.email)
        vote_info_dict = {"question_uuid": str(uuid1()),
                          "current_pleb": pleb.email, 'vote_type': 'up'}
        vote_response = vote_question_task.apply_async(kwargs=vote_info_dict)
        while not vote_response.ready():
            time.sleep(1)

        vote_response = vote_response.result

        self.assertEqual(type(vote_response), UnpickleableExceptionWrapper)

    def test_question_vote_task_already_connected(self):
        question = SBQuestion(content="test question from vote task test",
                              question_title="testquestiontitle from votetest",
                              question_id=uuid1())
        question.save()
        pleb = Pleb.nodes.get(email=self.user.email)
        vote_info_dict = {"question_uuid": question.question_id,
                          "current_pleb": pleb.email, 'vote_type': 'up'}
        question.up_voted_by.connect(pleb)
        vote_response = vote_question_task.apply_async(kwargs=vote_info_dict)
        while not vote_response.ready():
            time.sleep(1)
        vote_response = vote_response.result
        self.assertFalse(vote_response)

class TestMultipleTasks(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        self.question_info_dict = {'current_pleb': self.pleb.email,
                                   'question_title': "Test question",
                                   'content': 'test post',
                                   'question_uuid': str(uuid1())}

    def tearDown(self):
        call_command('clear_neo_db')

    def test_create_many_questions(self):
        print settings.CELERY_ALWAYS_EAGER
        if settings.CELERY_ALWAYS_EAGER:
            settings.CELERY_ALWAYS_EAGER = False
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
        print settings.CELERY_ALWAYS_EAGER
        if settings.CELERY_ALWAYS_EAGER:
            settings.CELERY_ALWAYS_EAGER = False
        question = SBQuestion(content="test question", question_title="title",
                              question_id=str(uuid1()))
        question.save()
        post_info_dict = {'current_pleb': self.pleb.email,
                          'question_title': 'Question Title',
                          'content': 'test question',
                          'question_uuid': question.question_id}
        response2 = create_question_task.apply_async(kwargs=post_info_dict)
        while not response2.ready():
            time.sleep(1)
        response2 = response2.result
        self.assertFalse(response2)
