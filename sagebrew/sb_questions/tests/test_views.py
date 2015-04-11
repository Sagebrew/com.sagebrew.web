from uuid import uuid1
from base64 import b64encode

from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from rest_framework.test import APIRequestFactory, APIClient

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_questions.neo_models import SBQuestion
from sb_questions.views import (save_question_view)


class SaveQuestionViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_save_question_view_correct_data(self):
        my_dict = {'content': 'aosdfhao',
                   'current_pleb': self.user.email,
                   'title': 'How do we end the war in Iraq?',
                   'tags': 'these,are,test,tags'}
        request = self.factory.post('/conversations/submit_question_api/',
                                    data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_question_view(request)

        self.assertEqual(response.status_code, 200)

    def test_save_question_view_missing_data(self):
        my_dict = {'content': 'aosdfhao',
                   'title': 'How do we end the war in Iraq?'}
        request = self.factory.post('/conversations/submit_question_api/',
                                    data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_question_view_int_data(self):
        my_dict = 98897965
        request = self.factory.post('/conversations/submit_question_api/',
                                    data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_question_view_string_data(self):
        my_dict = 'sdfasdfasdf'
        request = self.factory.post('/conversations/submit_question_api/',
                                    data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_question_view_list_data(self):
        my_dict = []
        request = self.factory.post('/conversations/submit_question_api/',
                                    data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_question_view_float_data(self):
        my_dict = 1.010101010
        request = self.factory.post('/conversations/submit_question_api/',
                                    data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_question_view_image_data(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/conversations/submit_question_api/',
                                    data=image,
                                    format='json')
        request.user = self.user
        response = save_question_view(request)

        self.assertEqual(response.status_code, 400)


class TestGetQuestionSearchView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.first_name = 'Tyler'
        self.pleb.last_name = 'Wiersing'
        self.pleb.save()
        self.client.force_authenticate(user=self.user)

    def test_get_question_search_view_success(self):
        question = SBQuestion(object_uuid=str(uuid1()), content='test',
                              title='test title').save()
        question.owned_by.connect(self.pleb)

        res = self.client.get('/conversations/search/%s/' %
                              question.object_uuid)
        res = res.render()
        self.assertTrue(res.content)
        self.assertEqual(res.status_code, 200)
