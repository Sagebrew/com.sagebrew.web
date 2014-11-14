from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import test_wait_util
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
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'current_pleb': self.user.email,
                                   'question_title': "Test question",
                                   'content': 'test post'}

    def test_save_question_util_success(self):
        response = create_question_util(**self.question_info_dict)

        self.assertIsNotNone(response)

    def test_save_question_util_pleb_does_not_exist(self):
        self.question_info_dict['current_pleb'] = 'adsfasdfasdfasdf@gmail.com'
        response = create_question_util(**self.question_info_dict)

        self.assertFalse(response)



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

        dict_response = get_question_by_uuid(question.sb_id,
                            current_pleb=self.question_info_dict
                            ['current_pleb'])

        self.assertIsInstance(dict_response, str)

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
            response = create_question_util(**self.question_info_dict)
            question_array.append(response)

        dict_response = get_question_by_least_recent(
                            current_pleb=self.question_info_dict
                            ['current_pleb'])

        self.assertIsInstance(dict_response, list)


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