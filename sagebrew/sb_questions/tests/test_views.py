from uuid import uuid1
from base64 import b64encode
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from api.utils import test_wait_util
from plebs.neo_models import Pleb
from sb_questions.views import (save_question_view, edit_question_view,
                                vote_question_view, get_question_view)
from sb_registration.utils import create_user_util

class SaveQuestionViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_save_question_view_correct_data(self):
        my_dict = {'content': 'aosdfhao',
                   'current_pleb': self.user.email,
                   'question_title': 'How do we end the war in Iraq?',
                   'tags': 'these,are,test,tags'}
        request = self.factory.post('/questions/submit_question_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_question_view(request)

        self.assertEqual(response.status_code, 200)

    def test_save_question_view_missing_data(self):
        my_dict = {'content': 'aosdfhao',
                   'question_title': 'How do we end the war in Iraq?'}
        request = self.factory.post('/questions/submit_question_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_question_view_int_data(self):
        my_dict = 98897965
        request = self.factory.post('/questions/submit_question_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_question_view_string_data(self):
        my_dict = 'sdfasdfasdf'
        request = self.factory.post('/questions/submit_question_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_question_view_list_data(self):
        my_dict = []
        request = self.factory.post('/questions/submit_question_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_question_view_float_data(self):
        my_dict = 1.010101010
        request = self.factory.post('/questions/submit_question_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_question_view_image_data(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/questions/submit_question_api/', data=image,
                                    format='json')
        request.user = self.user
        response = save_question_view(request)

        self.assertEqual(response.status_code, 400)

class EditQuestionViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_edit_question_view_correct_data(self):
        my_dict = {'content': 'aosdfhao',
                   'current_pleb': self.user.email,
                   'question_uuid': str(uuid1())}
        request = self.factory.post('/questions/edit_question_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = edit_question_view(request)

        self.assertEqual(response.status_code, 200)

    def test_edit_question_view_missing_data(self):
        my_dict = {'current_pleb': self.user.email,
                   'wall_pleb': self.user.email}
        request = self.factory.post('/questions/edit_question_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = edit_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_edit_question_view_int_data(self):
        my_dict = 98897965
        request = self.factory.post('/questions/edit_question_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = edit_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_edit_question_view_string_data(self):
        my_dict = 'sdfasdfasdf'
        request = self.factory.post('/questions/edit_question_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = edit_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_edit_question_view_list_data(self):
        my_dict = []
        request = self.factory.post('/questions/edit_question_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = edit_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_edit_question_view_float_data(self):
        my_dict = 1.010101010
        request = self.factory.post('/questions/edit_question_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = edit_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_edit_question_view_image_data(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/questions/edit_question_api/', data=image,
                                    format='json')
        request.user = self.user
        response = edit_question_view(request)

        self.assertEqual(response.status_code, 400)


class VoteQuestionViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_vote_question_view_correct_data(self):
        my_dict = {'current_pleb': self.user.email,
                   'vote_type': 'up',
                   'question_uuid': str(uuid1())}
        request = self.factory.post('/questions/vote_question_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = vote_question_view(request)

        self.assertEqual(response.status_code, 200)

    def test_vote_question_view_missing_data(self):
        my_dict = {'current_pleb': self.user.email,
                   'wall_pleb': self.user.email}
        request = self.factory.post('/questions/vote_question_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = vote_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_vote_question_view_int_data(self):
        my_dict = 98897965
        request = self.factory.post('/questions/vote_question_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = vote_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_vote_question_view_string_data(self):
        my_dict = 'sdfasdfasdf'
        request = self.factory.post('/questions/vote_question_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = vote_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_vote_question_view_list_data(self):
        my_dict = []
        request = self.factory.post('/questions/vote_question_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = vote_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_vote_question_view_float_data(self):
        my_dict = 1.010101010
        request = self.factory.post('/questions/vote_question_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = vote_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_vote_question_view_image_data(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/questions/vote_question_api/', data=image,
                                    format='json')
        request.user = self.user
        response = vote_question_view(request)

        self.assertEqual(response.status_code, 400)

class TestGetQuestionView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_get_question_view_correct_data(self):
        my_dict = {'current_pleb': 'tyler.wiersing@sagebrew.com',
                   'sort_by': 'most_recent'}
        request = self.factory.post('/questions/query_questions_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = get_question_view(request)

        self.assertEqual(response.status_code, 200)

    def test_get_question_view_missing_data(self):
        my_dict = {'current_pleb': self.user.email,
                   'wall_pleb': self.user.email}
        request = self.factory.post('/questions/query_questions_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = get_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_get_question_view_int_data(self):
        my_dict = 98897965
        request = self.factory.post('/questions/query_questions_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = vote_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_get_question_view_string_data(self):
        my_dict = 'sdfasdfasdf'
        request = self.factory.post('/questions/query_questions_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = get_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_get_question_view_list_data(self):
        my_dict = []
        request = self.factory.post('/questions/query_questions_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = get_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_get_question_view_float_data(self):
        my_dict = 1.010101010
        request = self.factory.post('/questions/query_questions_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = get_question_view(request)

        self.assertEqual(response.status_code, 400)

    def test_get_question_view_image_data(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/questions/query_questions_api/', data=image,
                                    format='json')
        request.user = self.user
        response = get_question_view(request)

        self.assertEqual(response.status_code, 400)