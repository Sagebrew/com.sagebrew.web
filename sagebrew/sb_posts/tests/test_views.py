import time
from datetime import datetime
from uuid import uuid1
from base64 import b64encode
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from django.test import TestCase

from plebs.neo_models import Pleb
from sb_posts.utils import save_post
from sb_posts.views import save_post_view, edit_post, delete_post, vote_post


class SavePostViewTests(TestCase):
    def setUp(self):
        try:
            pleb = Pleb.index.get(email='tyler.wiersing@gmail.com')
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
            self.factory = APIRequestFactory()
            self.user = User.objects.create_user(
                username='Tyler', email='tyler.wiersing@gmail.com')
        except Pleb.DoesNotExist:
            self.factory = APIRequestFactory()
            self.user = User.objects.create_user(
                username='Tyler', email='tyler.wiersing@gmail.com')

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
        with open("/home/apps/sagebrew/sb_posts/"
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/posts/submit_post/', data=image,
                                    format='json')
        request.user = self.user
        response = save_post_view(request)

        self.assertEqual(response.status_code, 400)

class EditPostViewTests(TestCase):
    def setUp(self):
        try:
            pleb = Pleb.index.get(email='tyler.wiersing@gmail.com')
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
            self.factory = APIRequestFactory()
            self.user = User.objects.create_user(
                username='Tyler', email='tyler.wiersing@gmail.com')
        except Pleb.DoesNotExist:
            self.factory = APIRequestFactory()
            self.user = User.objects.create_user(
                username='Tyler', email='tyler.wiersing@gmail.com')

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
        with open("/home/apps/sagebrew/sb_posts/"
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/posts/submit_post/', data=image,
                                    format='json')
        request.user = self.user
        response = edit_post(request)

        self.assertEqual(response.status_code, 400)

class DeletePostViewTests(TestCase):
    def setUp(self):
        try:
            pleb = Pleb.index.get(email='tyler.wiersing@gmail.com')
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
            self.factory = APIRequestFactory()
            self.user = User.objects.create_user(
                username='Tyler', email='tyler.wiersing@gmail.com')
        except Pleb.DoesNotExist:
            self.factory = APIRequestFactory()
            self.user = User.objects.create_user(
                username='Tyler', email='tyler.wiersing@gmail.com')

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
        with open("/home/apps/sagebrew/sb_posts/"
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/posts/submit_post/', data=image,
                                    format='json')
        request.user = self.user
        response = delete_post(request)

        self.assertEqual(response.status_code, 400)

class VotePostViewTests(TestCase):
    def setUp(self):
        try:
            pleb = Pleb.index.get(email='tyler.wiersing@gmail.com')
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
            self.factory = APIRequestFactory()
            self.user = User.objects.create_user(
                username='Tyler', email='tyler.wiersing@gmail.com')
        except Pleb.DoesNotExist:
            self.factory = APIRequestFactory()
            self.user = User.objects.create_user(
                username='Tyler', email='tyler.wiersing@gmail.com')

    def test_vote_post_view_correct_data(self):
        my_dict = {'pleb': self.user.email,
                   'vote_type': 'up',
                   'post_uuid': str(uuid1())}
        request = self.factory.post('/posts/vote_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = vote_post(request)

        self.assertEqual(response.status_code, 200)

    def test_vote_post_view_missing_data(self):
        my_dict = {'current_pleb': self.user.email,
                   'wall_pleb': self.user.email}
        request = self.factory.post('/posts/vote_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = vote_post(request)

        self.assertEqual(response.status_code, 400)

    def test_vote_post_view_int_data(self):
        my_dict = 98897965
        request = self.factory.post('/posts/vote_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = vote_post(request)

        self.assertEqual(response.status_code, 400)

    def test_vote_post_view_string_data(self):
        my_dict = 'sdfasdfasdf'
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = vote_post(request)

        self.assertEqual(response.status_code, 400)

    def test_vote_post_view_list_data(self):
        my_dict = []
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = vote_post(request)

        self.assertEqual(response.status_code, 400)

    def test_vote_post_view_float_data(self):
        my_dict = 1.010101010
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = vote_post(request)

        self.assertEqual(response.status_code, 400)

    def test_vote_post_view_image_data(self):
        with open("/home/apps/sagebrew/sb_posts/"
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/posts/submit_post/', data=image,
                                    format='json')
        request.user = self.user
        response = vote_post(request)

        self.assertEqual(response.status_code, 400)