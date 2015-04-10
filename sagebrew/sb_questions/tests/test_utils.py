from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework.test import APIRequestFactory, APIClient

from api.utils import wait_util
from sb_questions.utils import (create_question_util,
                                get_question_by_least_recent,
                                prepare_question_search_html)
from sb_questions.neo_models import SBQuestion
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test


class TestCreateQuestion(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.uuid = str(uuid1())
        self.question_info_dict = {'title': "Test question",
                                   'content': 'test post',
                                   'question_uuid': self.uuid}

    def test_save_question_util_success(self):
        response = create_question_util(**self.question_info_dict)

        self.assertIsNotNone(response)

    def test_save_question_twice(self):
        question = SBQuestion(title="Test question",
                              content="test post", object_uuid=self.uuid)
        question.save()
        response = create_question_util(**self.question_info_dict)

        self.assertEqual(response.object_uuid, question.object_uuid)


class TestGetQuestionByLeastRecent(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'title': "Test question",
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
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'title': "Test question",
                                   'content': 'test post',
                                   'object_uuid': str(uuid1())}
        self.pleb.first_name = "Tyler"
        self.pleb.last_name = "Wiersing"
        self.pleb.save()

    def test_prepare_question_search_html_success(self):
        request = self.factory.post('/questions/search/')
        request.user = self.user
        self.question_info_dict['object_uuid'] = str(uuid1())
        question = SBQuestion(**self.question_info_dict)
        question.save()
        question.owned_by.connect(self.pleb)
        question.save()
        

        res = prepare_question_search_html(question.object_uuid, request)

        self.assertTrue(res)

    def test_prepare_question_search_html_failure_question_does_not_exist(
            self):
        request = self.factory.post('/questions/search/')
        request.user = self.user
        res = prepare_question_search_html(str(uuid1()), request)

        self.assertFalse(res)