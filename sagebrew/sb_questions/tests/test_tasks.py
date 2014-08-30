import pytz
import time
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User

from sb_posts.utils import save_post, edit_post_info, delete_post_info
from sb_questions.tasks import (create_question_task, edit_question_task,
                                vote_question_task)
from sb_posts.neo_models import SBPost
from plebs.neo_models import Pleb


class TestSaveQuestionTask(TestCase):
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
                                   'content': 'test post'}

    def test_save_question_task(self):
        response = create_question_task.apply_async(kwargs=self.question_info_dict)

        self.assertTrue(response.get())

    def test_save_question_task_fail(self):
        question_info = {'current_pleb': self.pleb.email,
                         'question_title': "Test question"}
        response = create_question_task.apply_async(kwargs=question_info)

        self.assertFalse(response.get())

class TestEditQuestionTask(TestCase):
    def setUp(self):
        self.email = 'devon@sagebrew.com'
        try:
            pleb = Pleb.index.get(email=self.email)
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
        except Pleb.DoesNotExist:
            pass

        self.user = User.objects.create_user(
            username='Tyler' + str(uuid1())[:25], email=self.email)
        self.pleb = Pleb.index.get(email=self.email)

        self.question_info_dict = {'current_pleb': self.pleb.email,
                                   'question_title': "Test question",
                                   'content': 'test post',
                                   'question_uuid': str(uuid1())}
    def test_edit_post_task(self):
        edit_post_dict = {'content': 'question edited',
                          'question_uuid': self.question_info_dict['question_uuid'],
                          'current_pleb': self.pleb.email,
                          'last_edited_on': datetime.now(pytz.utc)}
        save_response = create_question_task.apply_async(kwargs=self.question_info_dict)
        time.sleep(1)
        edit_response = edit_question_task.apply_async(kwargs=edit_post_dict)

        self.assertTrue(save_response.get())
        self.assertTrue(edit_response.get())



class TestQuestionTaskRaceConditions(TestCase):
    def setUp(self):
        self.email = 'devon@sagebrew.com'
        try:
            pleb = Pleb.index.get(email=self.email)
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
        except Pleb.DoesNotExist:
            pass

        self.user = User.objects.create_user(
            username='Tyler' + str(uuid1())[:25], email=self.email)
        self.pleb = Pleb.index.get(email=self.email)

        self.question_info_dict = {'current_pleb': self.pleb.email,
                                   'question_title': "Test question",
                                   'content': 'test post',
                                   'question_uuid': str(uuid1())}

    def test_race_condition_edit_delete_post_tasks(self):
        edit_post_dict = {'content': 'Post edited',
                          'question_uuid': self.question_info_dict['question_uuid'],
                          'current_pleb': self.pleb.email,
                          'last_edited_on': datetime.now(pytz.utc)}
        save_response = create_question_task.apply_async(kwargs=self.question_info_dict)
        time.sleep(1)
        edit_response = edit_question_task.apply_async(kwargs=edit_post_dict)
        time.sleep(1)

        self.assertTrue(save_response.get())
        self.assertTrue(edit_response.get())

    def test_race_condition_edit_multiple_times(self):
        edit_array = []
        save_response = create_question_task.apply_async(kwargs=self.question_info_dict)

        edit_dict = {'content': "post edited",
                     'post_uuid': self.question_info_dict['question_uuid'],
                     'current_pleb': self.pleb.email,
                     'last_edited_on': datetime.now(pytz.utc)}
        for num in range(1, 10):
            edit_dict['content'] = "post edited" + str(num)
            edit_dict['last_edited_on'] = datetime.now(pytz.utc)
            edit_response = edit_question_task.apply_async(kwargs=edit_dict)
            edit_array.append(edit_response)

        self.assertTrue(save_response.get())
        for response in edit_array:
            self.assertTrue(response)

class TestVoteTask(TestCase):
    def setUp(self):
        self.email = 'devon@sagebrew.com'
        try:
            pleb = Pleb.index.get(email=self.email)
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
        except Pleb.DoesNotExist:
            pass

        self.user = User.objects.create_user(
            username='Tyler' + str(uuid1())[:25], email=self.email)
        self.pleb = Pleb.index.get(email=self.email)

        self.question_info_dict = {'current_pleb': self.pleb.email,
                                   'question_title': "Test question",
                                   'content': 'test post',
                                   'question_uuid': str(uuid1())}

    def test_question_vote_task(self):
        vote_info_dict = {"question_uuid": self.question_info_dict['question_uuid'],
                          "current_pleb": self.pleb.email, 'vote_type': 'up'}
        response = create_question_task.apply_async(kwargs=self.question_info_dict)
        response = response.get()

        vote_response = vote_question_task.apply_async(kwargs=vote_info_dict)
        self.assertTrue(response)
        self.assertTrue(vote_response.get())

class TestMultipleTasks(TestCase):
    def setUp(self):
        self.email = 'devon@sagebrew.com'
        try:
            pleb = Pleb.index.get(email=self.email)
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
        except Pleb.DoesNotExist:
            pass

        self.user = User.objects.create_user(
            username='Tyler' + str(uuid1())[:25], email=self.email)
        self.pleb = Pleb.index.get(email=self.email)

        self.question_info_dict = {'current_pleb': self.pleb.email,
                                   'question_title': "Test question",
                                   'content': 'test post',
                                   'question_uuid': str(uuid1())}

    def test_create_many_questions(self):
        response_array = []
        for num in range(1, 10):
            uuid = str(uuid1())
            self.question_info_dict['question_uuid'] = uuid
            save_response = create_question_task.apply_async(kwargs=self.question_info_dict)
            response_array.append(save_response.get())

        for item in response_array:
            self.assertTrue(item)



    def test_create_same_post_twice(self):
        post_info_dict = {'current_pleb': self.pleb.email,
                          'question_title': 'Question Title',
                          'content': 'test question',
                          'question_uuid': str(uuid1())}
        response1 = create_question_task.apply_async(kwargs=post_info_dict)
        time.sleep(1)
        response2 = create_question_task.apply_async(kwargs=post_info_dict)

        self.assertTrue(response1.get())
        self.assertFalse(response2.get())
