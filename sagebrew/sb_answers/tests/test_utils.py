import time
import pytz
from datetime import datetime, timedelta
from uuid import uuid1
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User

from plebs.neo_models import Pleb
from sb_answers.utils import (save_answer_util, edit_answer_util,
                              upvote_answer_util, downvote_answer_util)
from sb_answers.neo_models import SBAnswer
from sb_questions.neo_models import SBQuestion

class TestCreateAnswerUtil(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post'}
        self.answer_info_dict = {'question_uuid': '',
                                 'content': 'test answer',
                                 'answer_uuid': str(uuid1()),
                                 'current_pleb': self.user.email}
        while True:
            try:
                self.pleb = Pleb.nodes.get(email=self.user.email)
            except Exception:
                pass
            else:
                break

    def tearDown(self):
        call_command('clear_neo_db')


    def test_save_answer_util(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        self.answer_info_dict['question_uuid'] = question.question_id
        response = save_answer_util(**self.answer_info_dict)

        self.assertIsNot(response, False)

    def test_save_answer_util_empty_content(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        self.answer_info_dict['question_uuid'] = question.question_id
        self.answer_info_dict['content'] = ''
        response = save_answer_util(**self.answer_info_dict)

        self.assertFalse(response)

    def test_save_answer_util_question_does_not_exist(self):
        self.answer_info_dict['question_uuid'] = '246646156156615'
        response = save_answer_util(**self.answer_info_dict)

        self.assertEqual(response, None)

    def test_save_answer_util_pleb_does_not_exist(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        self.answer_info_dict['question_uuid'] = question.question_id
        self.answer_info_dict['current_pleb'] = 'adsfasd152fasdfasdf@gmail.com'
        response = save_answer_util(**self.answer_info_dict)

        self.assertFalse(response)

class TestEditAnswerUtil(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post'}
        self.answer_info_dict = {'question_uuid': '',
                                 'content': 'test answer',
                                 'answer_uuid': str(uuid1()),
                                 'current_pleb': self.user.email}
        while True:
            try:
                self.pleb = Pleb.nodes.get(email=self.user.email)
            except Exception:
                pass
            else:
                break

    def tearDown(self):
        call_command('clear_neo_db')

    def test_edit_answer_util(self):
        answer = SBAnswer(content="test answer", answer_id=str(uuid1()))
        answer.save()
        edit_answer_dict = {'current_pleb': self.question_info_dict['current_pleb'],
                            'content': 'edit content',
                            'last_edited_on': datetime.now(pytz.utc),
                            'answer_uuid': answer.answer_id}
        edit_response = edit_answer_util(**edit_answer_dict)

        self.assertTrue(edit_response)

    def test_edit_answer_util_to_be_deleted(self):
        answer = SBAnswer(content="test answer", answer_id=str(uuid1()))
        answer.to_be_deleted = True
        answer.save()

        edit_answer_dict = {'current_pleb': self.question_info_dict['current_pleb'],
                              'content': 'edit content',
                              'last_edited_on': datetime.now(pytz.utc),
                              'answer_uuid': answer.answer_id}
        edit_response = edit_answer_util(**edit_answer_dict)

        self.assertEqual(edit_response['detail'], 'to be deleted')

    def test_edit_answer_util_same_content(self):
        answer = SBAnswer(content="test answer", answer_id=str(uuid1()))
        answer.save()

        edit_answer_dict = {'current_pleb': self.question_info_dict['current_pleb'],
                              'content': 'test answer',
                              'last_edited_on': datetime.now(
                                  pytz.utc),
                              'answer_uuid': answer.answer_id}
        edit_response = edit_answer_util(**edit_answer_dict)

        self.assertEqual(edit_response['detail'], 'same content')

    def test_edit_answer_util_same_timestamp(self):
        now = datetime.now(pytz.utc)
        response = SBAnswer(content="test answer", answer_id=str(uuid1()))
        response.last_edited_on = now
        response.save()

        edit_answer_dict = {'current_pleb': self.question_info_dict['current_pleb'],
                              'content': 'test  question',
                              'last_edited_on': now,
                              'answer_uuid': response.answer_id}
        edit_response = edit_answer_util(**edit_answer_dict)

        self.assertEqual(edit_response['detail'], 'same timestamp')

    def test_edit_answer_util_more_recent_edit(self):
        now = datetime.now(pytz.utc)
        future_edit = now + timedelta(minutes=10)

        response = SBAnswer(content="test answer", answer_id=str(uuid1()))
        response.last_edited_on = future_edit
        response.save()

        edit_answer_dict = {'current_pleb': self.question_info_dict['current_pleb'],
                              'content': 'test     question',
                              'last_edited_on': now,
                              'answer_uuid': response.answer_id}
        edit_response = edit_answer_util(**edit_answer_dict)

        self.assertEqual(edit_response['detail'], 'last edit more recent')

    def test_edit_answer_util_question_does_not_exist(self):
        edit_answer_dict = {'current_pleb': self.question_info_dict['current_pleb'],
                              'content': 'test question',
                              'last_edited_on': datetime.now(pytz.utc),
                              'answer_uuid': str(uuid1())}
        edit_response = edit_answer_util(**edit_answer_dict)

        self.assertFalse(edit_response)

class TestVoteAnswerUtil(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post'}
        self.answer_info_dict = {'question_uuid': '',
                                 'content': 'test answer',
                                 'answer_uuid': str(uuid1()),
                                 'current_pleb': self.user.email}
        while True:
            try:
                self.pleb = Pleb.nodes.get(email=self.user.email)
            except Exception:
                pass
            else:
                break

    def tearDown(self):
        call_command('clear_neo_db')

    def test_upvote_answer_util(self):
        answer = SBAnswer(content="test answer", answer_id=str(uuid1()))
        answer.save()

        vote_response = upvote_answer_util(answer.answer_id,
                                             self.question_info_dict['current_pleb'])

        self.assertTrue(vote_response)

    def test_downvote_answer_util(self):
        answer = SBAnswer(content="test answer", answer_id=str(uuid1()))
        answer.save()

        vote_response = downvote_answer_util(answer.answer_id,
                                             self.question_info_dict['current_pleb'])

        self.assertTrue(vote_response)

    def test_downvote_answer_util_answer_dne(self):
        answer = SBAnswer(content="test answer", answer_id=str(uuid1()))
        answer.save()

        vote_response = downvote_answer_util(1,
                                             self.question_info_dict['current_pleb'])

        self.assertFalse(vote_response)

    def test_upvote_answer_util_answer_dne(self):
        answer = SBAnswer(content="test answer", answer_id=str(uuid1()))
        answer.save()

        vote_response = upvote_answer_util(1,
                                             self.question_info_dict['current_pleb'])

        self.assertFalse(vote_response)

    def test_downvote_answer_util_pleb_dne(self):
        answer = SBAnswer(content="test answer", answer_id=str(uuid1()))
        answer.save()

        vote_response = downvote_answer_util(answer.answer_id,
                                             'nope')

        self.assertFalse(vote_response)

    def test_upvote_answer_util_pleb_dne(self):
        answer = SBAnswer(content="test answer", answer_id=str(uuid1()))
        answer.save()

        vote_response = upvote_answer_util(answer.answer_id,
                                             'nope')

        self.assertFalse(vote_response)