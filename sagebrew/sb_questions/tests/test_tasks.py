import pytz
import time
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User

from sb_questions.tasks import (create_question_task, edit_question_task,
                                vote_question_task)
from plebs.neo_models import Pleb
from sb_questions.neo_models import SBQuestion


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
    def test_edit_question_task(self):

        question = SBQuestion(content="test question from edit task test",
                              question_title="testquestiontitle from edit test",
                              question_id=uuid1())
        question.save()
        edit_question_dict = {'content': 'question edited',
                          'question_uuid': question.question_id,
                          'current_pleb': self.email,
                          'last_edited_on': datetime.now(pytz.utc)}
        edit_response = edit_question_task.apply_async(kwargs=edit_question_dict)

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
        self.email = str(uuid1()) + '@sagebrew.com'
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
        question = SBQuestion(content="test question from vote task test",
                              question_title="testquestiontitle from vote test",
                              question_id=uuid1())
        question.save()
        pleb = Pleb.index.get(email=self.pleb.email)
        vote_info_dict = {"question_uuid": question.question_id,
                          "current_pleb": pleb.email, 'vote_type': 'up'}
        vote_response = vote_question_task.apply_async(kwargs=vote_info_dict)
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
        question = SBQuestion(content="test question", question_title="title",
                              question_id=str(uuid1()))
        question.save()
        post_info_dict = {'current_pleb': self.pleb.email,
                          'question_title': 'Question Title',
                          'content': 'test question',
                          'question_uuid': question.question_id}
        response2 = create_question_task.apply_async(kwargs=post_info_dict)

        self.assertFalse(response2.get())
