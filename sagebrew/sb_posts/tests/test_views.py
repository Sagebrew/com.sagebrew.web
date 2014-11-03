from uuid import uuid1
from base64 import b64encode
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from api.utils import test_wait_util
from plebs.neo_models import Pleb
from sb_posts.views import (save_post_view, edit_post, delete_post)
from sb_registration.utils import create_user_util


class SavePostViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_save_post_view_correct_data(self):
        my_dict = {'content': 'aosdfhao',
                   'current_pleb': self.user.email,
                   'wall_pleb': self.user.email}
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_post_view(request)

        self.assertEqual(response.status_code, 200)

    def test_save_post_view_missing_data(self):
        my_dict = {'current_pleb': self.user.email,
                   'wall_pleb': self.user.email}
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_post_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_post_view_int_data(self):
        my_dict = 98897965
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_post_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_post_view_string_data(self):
        my_dict = 'sdfasdfasdf'
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_post_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_post_view_list_data(self):
        my_dict = []
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_post_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_post_view_float_data(self):
        my_dict = 1.010101010
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_post_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_post_view_image_data(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/posts/submit_post/', data=image,
                                    format='json')
        request.user = self.user
        response = save_post_view(request)

        self.assertEqual(response.status_code, 400)

class EditPostViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_edit_post_view_correct_data(self):
        my_dict = {'content': 'aosdfhao',
                   'current_pleb': self.user.email,
                   'wall_pleb': self.user.email,
                   'post_uuid': str(uuid1())}
        request = self.factory.post('/posts/edit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = edit_post(request)

        self.assertEqual(response.status_code, 200)

    def test_edit_post_view_missing_data(self):
        my_dict = {'current_pleb': self.user.email,
                   'wall_pleb': self.user.email}
        request = self.factory.post('/posts/edit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = edit_post(request)

        self.assertEqual(response.status_code, 400)

    def test_edit_post_view_int_data(self):
        my_dict = 98897965
        request = self.factory.post('/posts/edit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = edit_post(request)

        self.assertEqual(response.status_code, 400)

    def test_edit_post_view_string_data(self):
        my_dict = 'sdfasdfasdf'
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = edit_post(request)

        self.assertEqual(response.status_code, 400)

    def test_edit_post_view_list_data(self):
        my_dict = []
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = edit_post(request)

        self.assertEqual(response.status_code, 400)

    def test_edit_post_view_float_data(self):
        my_dict = 1.010101010
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = edit_post(request)

        self.assertEqual(response.status_code, 400)

    def test_edit_post_view_image_data(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/posts/submit_post/', data=image,
                                    format='json')
        request.user = self.user
        response = edit_post(request)

        self.assertEqual(response.status_code, 400)

class DeletePostViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_delete_post_view_correct_data(self):
        my_dict = {'pleb': self.user.email,
                   'post_uuid': str(uuid1())}
        request = self.factory.post('/posts/delete_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = delete_post(request)

        self.assertEqual(response.status_code, 200)

    def test_delete_post_view_missing_data(self):
        my_dict = {'current_pleb': self.user.email,
                   'wall_pleb': self.user.email}
        request = self.factory.post('/posts/delete_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = delete_post(request)

        self.assertEqual(response.status_code, 400)

    def test_delete_post_view_int_data(self):
        my_dict = 98897965
        request = self.factory.post('/posts/delete_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = delete_post(request)

        self.assertEqual(response.status_code, 400)

    def test_delete_post_view_string_data(self):
        my_dict = 'sdfasdfasdf'
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = delete_post(request)

        self.assertEqual(response.status_code, 400)

    def test_delete_post_view_list_data(self):
        my_dict = []
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = delete_post(request)

        self.assertEqual(response.status_code, 400)

    def test_delete_post_view_float_data(self):
        my_dict = 1.010101010
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = delete_post(request)

        self.assertEqual(response.status_code, 400)

    def test_delete_post_view_image_data(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/posts/submit_post/', data=image,
                                    format='json')
        request.user = self.user
        response = delete_post(request)

        self.assertEqual(response.status_code, 400)