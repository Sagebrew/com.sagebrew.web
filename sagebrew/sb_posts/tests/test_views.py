import pytz
from uuid import uuid1
from datetime import datetime, timedelta
from base64 import b64encode
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_posts.views import (save_post_view, get_user_posts)
from sb_registration.utils import create_user_util_test
from sb_posts.neo_models import SBPost


class SavePostViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
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

class TestGetUserPosts(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_get_user_posts(self):
        for item in range(0, 3):
            post = SBPost(
                content='test', object_uuid=str(uuid1()),
                created=(datetime.now(pytz.utc) + timedelta(hours=10))).save()
            rel = post.owned_by.connect(self.pleb)
            rel.save()
            self.pleb.wall.all()[0].post.connect(post)

        data = {'current_user': self.pleb.username,
                'range_end': 1,
                'range_start': 0}
        request = self.factory.post('/posts/query_posts/', data=data,
                                    format='json')
        request.user = self.user
        res = get_user_posts(request)

        self.assertEqual(res.status_code, 200)

    def test_get_user_posts_invalid_form(self):
        data = {'curreasdfnt_user': self.pleb.email,
                'email': self.pleb.email,
                'range_end': 5,
                'range_start': 0}
        request = self.factory.post('/posts/query_posts/', data=data,
                                    format='json')
        request.user = self.user
        res = get_user_posts(request)

        self.assertEqual(res.status_code, 400)
