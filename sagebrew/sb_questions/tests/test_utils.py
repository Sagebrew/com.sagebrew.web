import time
import pytz
from datetime import datetime, timedelta
from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from sb_questions.utils import (create_question_util, upvote_question_util,
                                downvote_question_util, edit_question_util,
                                prepare_get_question_dictionary)
from plebs.neo_models import Pleb

class TestCreateQuestion(TestCase):
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

    def test_save_question_util_success(self):
        response = create_question_util(**self.question_info_dict)

        self.assertIsNotNone(response)

    def test_save_question_util_empty_content(self):
        self.question_info_dict['content'] = ''
        response = create_question_util(**self.question_info_dict)

        self.assertIsNone(response)

    def test_save_question_util_empty_title(self):
        self.question_info_dict['question_title'] = ''
        response = create_question_util(**self.question_info_dict)

        self.assertIsNone(response)

    def test_save_question_util_pleb_does_not_exist(self):
        self.question_info_dict['current_pleb'] = 'adsfasdfasdfasdf@gmail.com'
        response = create_question_util(**self.question_info_dict)

        self.assertIsNone(response)

class TestPrepareQuestionDictUtil(TestCase):
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

    def test_get_question_dict_by_uuid(self):
        response = create_question_util(**self.question_info_dict)

        dict_response = prepare_get_question_dictionary(response,
                            sort_by='uuid',
                            current_pleb=self.question_info_dict['current_pleb'])

        self.assertIsInstance(dict_response, dict)

    def test_get_questions(self):
        question_array = []
        for num in range(1,5):
            self.question_info_dict['question_uuid'] = str(uuid1())
            response = create_question_util(**self.question_info_dict)
            question_array.append(response)

        dict_response = prepare_get_question_dictionary(question_array,
                            sort_by='most_recent',
                            current_pleb=self.question_info_dict['current_pleb'])

        self.assertIsInstance(dict_response, list)

class TestEditQuestionUtils(TestCase):
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
                                   'content': 'test question',
                                   'question_uuid': str(uuid1())}

    def test_edit_question_util(self):
        response = create_question_util(**self.question_info_dict)

        edit_question_dict = {'current_pleb': self.question_info_dict['current_pleb'],
                              'content': 'edit content',
                              'last_edited_on': datetime.now(pytz.utc),
                              'question_uuid': response.question_id}
        edit_response = edit_question_util(**edit_question_dict)

        self.assertTrue(edit_response)

    def test_edit_question_util_to_be_deleted(self):
        response = create_question_util(**self.question_info_dict)
        response.to_be_deleted = True
        response.save()

        edit_question_dict = {'current_pleb': self.question_info_dict['current_pleb'],
                              'content': 'edit content',
                              'last_edited_on': datetime.now(pytz.utc),
                              'question_uuid': response.question_id}
        edit_response = edit_question_util(**edit_question_dict)

        self.assertEqual(edit_response['detail'], 'to be deleted')

    def test_edit_question_util_same_content(self):
        response = create_question_util(**self.question_info_dict)

        edit_question_dict = {'current_pleb': self.question_info_dict['current_pleb'],
                              'content': 'test question',
                              'last_edited_on': datetime.now(pytz.utc),
                              'question_uuid': response.question_id}
        edit_response = edit_question_util(**edit_question_dict)

        self.assertEqual(edit_response['detail'], 'same content')

    def test_edit_question_util_same_timestamp(self):
        now = datetime.now(pytz.utc)
        response = create_question_util(**self.question_info_dict)
        response.last_edited_on = now
        response.save()

        edit_question_dict = {'current_pleb': self.question_info_dict['current_pleb'],
                              'content': 'test  question',
                              'last_edited_on': now,
                              'question_uuid': response.question_id}
        edit_response = edit_question_util(**edit_question_dict)

        self.assertEqual(edit_response['detail'], 'same timestamp')

    def test_edit_question_util_more_recent_edit(self):
        now = datetime.now(pytz.utc)
        future_edit = now + timedelta(minutes=10)

        response = create_question_util(**self.question_info_dict)
        response.last_edited_on = future_edit
        response.save()

        edit_question_dict = {'current_pleb': self.question_info_dict['current_pleb'],
                              'content': 'test     question',
                              'last_edited_on': now,
                              'question_uuid': response.question_id}
        edit_response = edit_question_util(**edit_question_dict)

        self.assertEqual(edit_response['detail'], 'last edit more recent')

    def test_edit_question_util_question_does_not_exist(self):
        edit_question_dict = {'current_pleb': self.question_info_dict['current_pleb'],
                              'content': 'test question',
                              'last_edited_on': datetime.now(pytz.utc),
                              'question_uuid': self.question_info_dict['question_uuid']}
        edit_response = edit_question_util(**edit_question_dict)

        self.assertFalse(edit_response)

class TestVoteQuestionUtil(TestCase):
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
                                   'content': 'test question',
                                   'question_uuid': str(uuid1())}

    def test_upvote_question_util(self):
        response = create_question_util(**self.question_info_dict)
        vote_response = upvote_question_util(response.question_id,
                                             self.question_info_dict['current_pleb'])

        self.assertTrue(vote_response)

    def test_downvote_question_util(self):
        response = create_question_util(**self.question_info_dict)
        vote_response = downvote_question_util(response.question_id,
                                             self.question_info_dict['current_pleb'])

        self.assertTrue(vote_response)

    def test_downvote_question_util_question_dne(self):
        response = create_question_util(**self.question_info_dict)

        vote_response = downvote_question_util(uuid1(),
                                             self.question_info_dict['current_pleb'])

        self.assertFalse(vote_response)

    def test_upvote_question_util_question_dne(self):
        response = create_question_util(**self.question_info_dict)

        vote_response = upvote_question_util(uuid1(),
                                             self.question_info_dict['current_pleb'])

        self.assertFalse(vote_response)

    def test_downvote_question_util_pleb_dne(self):
        response = create_question_util(**self.question_info_dict)

        vote_response = downvote_question_util(self.question_info_dict['question_uuid'],
                                             'nope')

        self.assertFalse(vote_response)

    def test_upvote_question_util_pleb_dne(self):
        response = create_question_util(**self.question_info_dict)

        vote_response = upvote_question_util(self.question_info_dict['question_uuid'],
                                             'nope')

        self.assertFalse(vote_response)


