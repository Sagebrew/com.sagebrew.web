from uuid import uuid1
from base64 import b64encode
import requests_mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from rest_framework.test import APIRequestFactory

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_comments.views import save_comment_view
from sb_registration.utils import create_user_util_test


class TestSaveCommentView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    @requests_mock.mock()
    def test_save_comment_view_correct_data(self, m):
        my_dict = {'content': 'testastdat', 'object_uuid': str(uuid1()),
                   'object_type': '01bb301a-644f-11e4-9ad9-080027242395',
                   'current_pleb': self.user.email}
        request = self.factory.post('/comments/submit_comment/', data=my_dict,
                                    format='json')
        request.user = self.user
        m.get('http://testserver/v1/users/test_test/?expand=True',
              json={
                  'username': 'test_test',
                  'profile': {
                      'profile_pic': None,
                      'base_user': 'https://192.168.56.101/v1/users/test_test/',
                      'href': 'https://192.168.56.101/v1/profiles/test_test/',
                      'url': 'https://192.168.56.101/user/test_test/'
                   },
                  'first_name': 'test',
                  'last_name': 'test',
                  'href': 'https://192.168.56.101/v1/users/test_test/'
            })
        response = save_comment_view(request)

        self.assertEqual(response.status_code, 200)

    def test_save_comment_view_missing_data(self):
        my_dict = {'content': 'testastdat',
                   'pleb': self.user.email}
        request = self.factory.post('/comments/submit_comment/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_comment_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_comment_view_int_data(self):
        request = self.factory.post('/comments/submit_comment/', data=64816,
                                    format='json')
        request.user = self.user
        response = save_comment_view(request)

        self.assertEqual(response.status_code, 400)

    @requests_mock.mock()
    def test_save_comment_view_string_data(self, m):
        my_dict = 'sdfasdfasdf'
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        m.get('http://testserver/v1/users/test_test/?expand=True',
              json={
                  'username': 'test_test',
                  'profile': {
                      'profile_pic': None,
                      'base_user': 'https://192.168.56.101/v1/users/test_test/',
                      'href': 'https://192.168.56.101/v1/profiles/test_test/',
                      'url': 'https://192.168.56.101/user/test_test/'
                   },
                  'first_name': 'test',
                  'last_name': 'test',
                  'href': 'https://192.168.56.101/v1/users/test_test/'
            })
        response = save_comment_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_comment_view_list_data(self):
        my_dict = []
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_comment_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_comment_view_float_data(self):
        my_dict = 1.010101010
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_comment_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_comment_view_image_data(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/posts/submit_post/', data=image,
                                    format='json')
        request.user = self.user
        response = save_comment_view(request)

        self.assertEqual(response.status_code, 400)



