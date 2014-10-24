import pytz
from datetime import datetime, timedelta
from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import test_wait_util
from sb_answers.neo_models import SBAnswer
from sb_questions.utils import (create_question_util, upvote_question_util,
                                downvote_question_util, edit_question_util,
                                prepare_get_question_dictionary,
                                get_question_by_uuid,
                                get_question_by_least_recent,
                                flag_question_util,
                                prepare_question_search_html)
from sb_questions.neo_models import SBQuestion
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util

class TestCreateQuestion(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post'}

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
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post'}

    def test_get_question_dict_by_uuid(self):
        self.question_info_dict.pop('question_uuid',None)
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(question_id=str(uuid1()))
        question.save()
        question.owned_by.connect(self.pleb)
        question.save()
        dict_response = prepare_get_question_dictionary(question,
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

    def test_get_question_with_answers(self):
        self.question_info_dict.pop('question_uuid',None)
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(question_id=str(uuid1()))
        question.save()
        question.owned_by.connect(self.pleb)
        question.save()
        answer = SBAnswer(answer_id=str(uuid1())).save()
        answer.owned_by.connect(self.pleb)
        answer.save()
        question.answer.connect(answer)
        question.save()

        dict_response = prepare_get_question_dictionary(question,
                            sort_by='uuid',
                            current_pleb=self.question_info_dict['current_pleb'])

        self.assertIsInstance(dict_response, dict)

class TestGetQuestionByUUID(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post'}

    def test_get_question_by_uuid_success(self):
        self.question_info_dict.pop('question_uuid',None)
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(question_id=str(uuid1()))
        question.save()
        question.owned_by.connect(self.pleb)
        question.save()
        answer = SBAnswer(answer_id=str(uuid1())).save()
        answer.owned_by.connect(self.pleb)
        answer.save()
        question.answer.connect(answer)
        question.save()

        dict_response = get_question_by_uuid(question.question_id,
                            current_pleb=self.question_info_dict
                            ['current_pleb'])

        self.assertIsInstance(dict_response, dict)

    def test_get_question_by_uuid_failure_question_does_not_exist(self):

        dict_response = get_question_by_uuid(str(uuid1()),
                            current_pleb=self.question_info_dict
                            ['current_pleb'])

        self.assertIsInstance(dict_response, dict)
        self.assertEqual(dict_response['detail'],
                         'There are no questions with that ID')


class TestGetQuestionByLeastRecent(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post'}

    def test_get_questions_by_least_recent_success(self):
        question_array = []
        for num in range(1,5):
            self.question_info_dict['question_uuid'] = str(uuid1())
            response = create_question_util(**self.question_info_dict)
            question_array.append(response)

        dict_response = get_question_by_least_recent(
                            current_pleb=self.question_info_dict
                            ['current_pleb'])

        self.assertIsInstance(dict_response, list)

class TestEditQuestionUtils(TestCase):
    def setUp(self):
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

    def test_edit_question_util(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(question_id=str(uuid1()), content="test",
                              question_title='Test Title')
        question.save()

        edit_question_dict = {'current_pleb': self.question_info_dict['current_pleb'],
                              'content': 'edit content',
                              'last_edited_on': datetime.now(pytz.utc),
                              'question_uuid': question.question_id}
        edit_response = edit_question_util(**edit_question_dict)

        self.assertTrue(edit_response)

    def test_edit_question_util_to_be_deleted(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(question_id=str(uuid1()), content="test",
                              question_title='Test Title')
        question.save()
        question.to_be_deleted = True
        question.save()

        edit_question_dict = {'current_pleb': self.question_info_dict['current_pleb'],
                              'content': 'edit content',
                              'last_edited_on': datetime.now(pytz.utc),
                              'question_uuid': question.question_id}
        edit_response = edit_question_util(**edit_question_dict)

        self.assertEqual(edit_response['detail'], 'to be deleted')

    def test_edit_question_util_same_content(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()

        edit_question_dict = {'current_pleb': self.question_info_dict['current_pleb'],
                              'content': 'test post',
                              'last_edited_on': datetime.now(pytz.utc),
                              'question_uuid': question.question_id}
        edit_response = edit_question_util(**edit_question_dict)

        self.assertEqual(edit_response['detail'], 'same content')

    def test_edit_question_util_same_timestamp(self):
        now = datetime.now(pytz.utc)
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(question_id=str(uuid1()), content="test",
                              question_title='Test Title')
        question.save()
        question.last_edited_on = now
        question.save()

        edit_question_dict = {'current_pleb': self.question_info_dict['current_pleb'],
                              'content': 'test  question',
                              'last_edited_on': now,
                              'question_uuid': question.question_id}
        edit_response = edit_question_util(**edit_question_dict)

        self.assertEqual(edit_response['detail'], 'same timestamp')

    def test_edit_question_util_more_recent_edit(self):
        now = datetime.now(pytz.utc)
        future_edit = now + timedelta(minutes=10)

        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(question_id=str(uuid1()),content="test",
                              question_title='Test Title')
        question.save()
        question.last_edited_on = future_edit
        question.save()

        edit_question_dict = {'current_pleb': self.question_info_dict['current_pleb'],
                              'content': 'test     question',
                              'last_edited_on': now,
                              'question_uuid': question.question_id}
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

    def test_upvote_question_util(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        vote_response = upvote_question_util(question.question_id,
                                             self.question_info_dict['current_pleb'])

        self.assertTrue(vote_response)

    def test_downvote_question_util(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        vote_response = downvote_question_util(question.question_id,
                                             self.question_info_dict['current_pleb'])

        self.assertTrue(vote_response)

    def test_downvote_question_util_question_dne(self):
        vote_response = downvote_question_util(uuid1(),
                                             self.question_info_dict['current_pleb'])

        self.assertFalse(vote_response)

    def test_upvote_question_util_question_dne(self):
        vote_response = upvote_question_util(uuid1(),
                                             self.question_info_dict['current_pleb'])

        self.assertFalse(vote_response)

    def test_downvote_question_util_pleb_dne(self):
        response = create_question_util(**self.question_info_dict)

        vote_response = downvote_question_util(self.question_info_dict['question_uuid'],
                                             'nope')

        self.assertEqual(vote_response, None)

    def test_upvote_question_util_pleb_dne(self):
        response = create_question_util(**self.question_info_dict)

        vote_response = upvote_question_util(self.question_info_dict['question_uuid'],
                                             'nope')

        self.assertEqual(vote_response, None)


class TestFlagQuestionUtil(TestCase):
    def setUp(self):
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

    def test_flag_question_util_success_spam(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()

        res = flag_question_util(question.question_id, self.pleb.email,
                                 'spam')

        self.assertTrue(res)

    def test_flag_question_util_success_explicit(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()

        res = flag_question_util(question.question_id, self.pleb.email,
                                 'explicit')

        self.assertTrue(res)

    def test_flag_question_util_success_other(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()

        res = flag_question_util(question.question_id, self.pleb.email,
                                 'other')

        self.assertTrue(res)

    def test_flag_question_util_success_duplicate(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()

        res = flag_question_util(question.question_id, self.pleb.email,
                                 'duplicate')

        self.assertTrue(res)

    def test_flag_question_util_success_changed(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()

        res = flag_question_util(question.question_id, self.pleb.email,
                                 'changed')

        self.assertTrue(res)

    def test_flag_question_util_success_unsupported(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()

        res = flag_question_util(question.question_id, self.pleb.email,
                                 'unsupported')

        self.assertTrue(res)

    def test_flag_question_util_success_user_already_flagged(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        question.flagged_by.connect(self.pleb)
        res = flag_question_util(question.question_id, self.pleb.email,
                                 'unsupported')

        self.assertTrue(res)

    def test_flag_question_util_failure_invalid_reason(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        res = flag_question_util(question.question_id, self.pleb.email,
                                 'dumb')

        self.assertFalse(res)

    def test_flag_question_util_failure_question_does_not_exist(self):
        res = flag_question_util(str(uuid1()), self.pleb.email,
                                 'unsupported')

        self.assertFalse(res)

    def test_flag_question_util_failure_pleb_does_not_exist(self):
        self.question_info_dict['question_id']=str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()

        res = flag_question_util(question.question_id, str(uuid1()),
                                 'unsupported')

        self.assertIsNone(res)


class TestPrepareQuestionSearchHTML(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'question_title': "Test question",
                                   'content': 'test post',
                                   'question_id': str(uuid1())}
        self.pleb.first_name = "Tyler"
        self.pleb.last_name = "Wiersing"
        self.pleb.save()

    def test_prepare_question_search_html_success(self):
        self.question_info_dict['question_id'] = str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        question.owned_by.connect(self.pleb)
        question.save()

        res = prepare_question_search_html(question.question_id)

        self.assertTrue(res)

    def test_prepare_question_search_html_failure_question_does_not_exist(self):
        res = prepare_question_search_html(str(uuid1()))

        self.assertFalse(res)