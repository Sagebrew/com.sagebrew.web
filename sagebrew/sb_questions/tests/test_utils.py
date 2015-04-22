from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework.test import APIRequestFactory

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_questions.utils import (prepare_question_search_html)
from sb_questions.neo_models import Question


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
        question = Question(**self.question_info_dict)
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
