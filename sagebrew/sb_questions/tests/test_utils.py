from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.safestring import SafeText

from api.utils import wait_util
from sb_answers.neo_models import SBAnswer
from sb_questions.utils import (create_question_util,
                                get_question_by_uuid,
                                get_question_by_least_recent,
                                prepare_question_search_html)
from sb_questions.neo_models import SBQuestion
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util


class TestCreateQuestion(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.uuid = str(uuid1())
        self.question_info_dict = {'question_title': "Test question",
                                   'content': 'test post',
                                   'question_uuid': self.uuid}

    def test_save_question_util_success(self):
        response = create_question_util(**self.question_info_dict)

        self.assertIsNotNone(response)

    def test_save_question_twice(self):
        question = SBQuestion(question_title="Test question",
                              content="test post", sb_id=self.uuid)
        question.save()
        response = create_question_util(**self.question_info_dict)

        self.assertEqual(response.sb_id, question.sb_id)


class TestGetQuestionByUUID(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post'}

    def test_get_question_by_uuid_success(self):
        self.question_info_dict.pop('question_uuid',None)
        self.question_info_dict['sb_id']=str(uuid1())
        question = SBQuestion(sb_id=str(uuid1()))
        question.save()
        question.owned_by.connect(self.pleb)
        question.save()
        answer = SBAnswer(sb_id=str(uuid1())).save()
        answer.owned_by.connect(self.pleb)
        answer.save()
        question.answer.connect(answer)
        question.save()

        response = get_question_by_uuid(
            question.sb_id, current_pleb=self.question_info_dict['current_pleb'])

        self.assertIsInstance(response, SafeText)

    def test_get_question_by_uuid_failure_question_does_not_exist(self):

        question_uuid = get_question_by_uuid(
            str(uuid1()), current_pleb=self.question_info_dict['current_pleb'])

        self.assertFalse(question_uuid, False)


class TestGetQuestionByLeastRecent(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'question_title': "Test question",
                                   'content': 'test post',
                                   'question_uuid': str(uuid1())}

    def test_get_questions_by_least_recent_success(self):
        question_array = []
        for num in range(1, 5):
            response = create_question_util(**self.question_info_dict)
            question_array.append(response)

        dict_response = get_question_by_least_recent()

        self.assertIsInstance(dict_response, list)


class TestPrepareQuestionSearchHTML(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'question_title': "Test question",
                                   'content': 'test post',
                                   'sb_id': str(uuid1())}
        self.pleb.first_name = "Tyler"
        self.pleb.last_name = "Wiersing"
        self.pleb.save()

    def test_prepare_question_search_html_success(self):
        self.question_info_dict['sb_id'] = str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        question.owned_by.connect(self.pleb)
        question.save()

        res = prepare_question_search_html(question.sb_id)

        self.assertTrue(res)

    def test_prepare_question_search_html_failure_question_does_not_exist(self):
        res = prepare_question_search_html(str(uuid1()))

        self.assertFalse(res)