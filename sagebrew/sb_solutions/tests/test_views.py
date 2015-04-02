from base64 import b64encode
from rest_framework.test import APIRequestFactory

import requests_mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from api.utils import wait_util
from sb_solutions.views import save_solution_view
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test


class TestSaveSolutionView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    @requests_mock.mock()
    def test_save_solution_view_correct_data(self, m):
        my_dict = {'content': 'test solution', 'question_uuid': '12312'}

        request = self.factory.post('/solutions/submit_solution_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        m.get('http://testserver/v1/users/test_test/?expand=True',
              json={
                  'username': 'test_test',
                  'profile': {
                      'profile_pic': None,
                      'base_user': 'https://192.168.56.101/v1/users/test_test/',
                      'href': 'https://192.168.56.101/v1/profiles/test_test/',
                      'profile_url': 'https://192.168.56.101/user/test_test/'
                   },
                  'first_name': 'test',
                  'last_name': 'test',
                  'href': 'https://192.168.56.101/v1/users/test_test/'
            })
        response = save_solution_view(request)
        # TODO need to figure out the best way to assert that only one solution
        # is being saved and returned.
        self.assertEqual(response.status_code, 200)

    def test_save_solution_view_missing_data(self):
        my_dict = {'question_uuid': '12312'}

        request = self.factory.post('/solutions/submit_solution_api/', data=my_dict,
                                    format='json')
        request.user = self.user

        response = save_solution_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_solution_view_int_data(self):
        my_dict = 98897965
        request = self.factory.post('/solutions/submit_solution_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_solution_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_solution_view_string_data(self):
        my_dict = 'sdfasdfasdf'
        request = self.factory.post('/solutions/submit_solution_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_solution_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_solution_view_list_data(self):
        my_dict = []
        request = self.factory.post('/solutions/submit_solution_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_solution_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_solution_view_float_data(self):
        my_dict = 1.010101010
        request = self.factory.post('/solutions/submit_solution_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_solution_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_solution_view_image_data(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/solutions/submit_solution_api/', data=image,
                                    format='json')
        request.user = self.user
        response = save_solution_view(request)

        self.assertEqual(response.status_code, 400)

