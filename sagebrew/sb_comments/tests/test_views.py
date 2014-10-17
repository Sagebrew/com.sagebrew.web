from uuid import uuid1
from base64 import b64encode
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.conf import settings

from plebs.neo_models import Pleb
from sb_comments.views import (save_comment_view, edit_comment, delete_comment,
                               vote_comment, flag_comment)


class TestSaveCommentView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        while True:
            try:
                self.pleb = Pleb.nodes.get(email=self.user.email)
            except Exception:
                pass
            else:
                break

    def tearDown(self):
        call_command('clear_neo_db')

    def test_save_comment_view_correct_data(self):
        my_dict = {'content': 'testastdat', 'post_uuid': str(uuid1()),
                   'pleb': self.user.email}
        request = self.factory.post('/comments/submit_comment/', data=my_dict,
                                    format='json')
        request.user = self.user
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

    def test_save_comment_view_string_data(self):
        my_dict = 'sdfasdfasdf'
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
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

class TestEditCommentView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        while True:
            try:
                self.pleb = Pleb.nodes.get(email=self.user.email)
            except Exception:
                pass
            else:
                break

    def tearDown(self):
        call_command('clear_neo_db')

    def test_edit_comment_view_correct_data(self):
        my_dict = {'content': 'testastdat', 'comment_uuid': str(uuid1()),
                   'pleb': self.user.email}
        request = self.factory.post('/comments/edit_comment/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = edit_comment(request)

        self.assertEqual(response.status_code, 200)

    def test_edit_comment_view_missing_data(self):
        my_dict = {'comment_uuid': str(uuid1()),
                   'pleb': self.user.email}
        request = self.factory.post('/comments/edit_comment/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = edit_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_edit_comment_view_int_data(self):
        request = self.factory.post('/comments/edit_comment/', data=64816,
                                    format='json')
        request.user = self.user
        response = edit_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_edit_comment_view_string_data(self):
        my_dict = 'sdfasdfasdf'
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = edit_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_edit_comment_view_list_data(self):
        my_dict = []
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = edit_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_edit_comment_view_float_data(self):
        my_dict = 1.010101010
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = edit_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_edit_comment_view_image_data(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/posts/submit_post/', data=image,
                                    format='json')
        request.user = self.user
        response = edit_comment(request)

        self.assertEqual(response.status_code, 400)

class TestDeleteCommentView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        while True:
            try:
                self.pleb = Pleb.nodes.get(email=self.user.email)
            except Exception:
                pass
            else:
                break

    def tearDown(self):
        call_command('clear_neo_db')

    def test_delete_comment_view_correct_data(self):
        my_dict = {'comment_uuid': str(uuid1()),
                   'pleb': self.user.email}
        request = self.factory.post('/comments/delete_comment/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = delete_comment(request)

        self.assertEqual(response.status_code, 200)

    def test_delete_comment_view_missing_data(self):
        my_dict = {'pleb': self.user.email}
        request = self.factory.post('/comments/delete_comment/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = delete_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_delete_comment_view_int_data(self):
        request = self.factory.post('/comments/delete_comment/', data=64816,
                                    format='json')
        request.user = self.user
        response = delete_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_delete_comment_view_string_data(self):
        my_dict = 'sdfasdfasdf'
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = delete_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_delete_comment_view_list_data(self):
        my_dict = []
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = delete_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_delete_comment_view_float_data(self):
        my_dict = 1.010101010
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = delete_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_delete_comment_view_image_data(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/posts/submit_post/', data=image,
                                    format='json')
        request.user = self.user
        response = delete_comment(request)

        self.assertEqual(response.status_code, 400)

class TestVoteCommentView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        while True:
            try:
                self.pleb = Pleb.nodes.get(email=self.user.email)
            except Exception:
                pass
            else:
                break

    def tearDown(self):
        call_command('clear_neo_db')

    def test_vote_comment_view_correct_data(self):
        my_dict = {'comment_uuid': str(uuid1()),
                   'pleb': self.user.email, 'vote_type': 'up'}
        request = self.factory.post('/comments/vote_comment/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = vote_comment(request)

        self.assertEqual(response.status_code, 200)

    def test_vote_comment_view_missing_data(self):
        my_dict = {'vote_type': 'up'}
        request = self.factory.post('/comments/vote_comment/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = vote_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_vote_comment_view_int_data(self):
        request = self.factory.post('/comments/vote_comment/', data=123456789,
                                    format='json')
        request.user = self.user
        response = vote_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_vote_comment_view_string_data(self):
        my_dict = 'sdfasdfasdf'
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = vote_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_vote_comment_view_list_data(self):
        my_dict = []
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = vote_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_vote_comment_view_float_data(self):
        my_dict = 1.010101010
        request = self.factory.post('/posts/submit_post/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = vote_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_vote_comment_view_image_data(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/posts/submit_post/', data=image,
                                    format='json')
        request.user = self.user
        response = vote_comment(request)

        self.assertEqual(response.status_code, 400)


class TestFlagCommentView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        while True:
            try:
                self.pleb = Pleb.nodes.get(email=self.user.email)
            except Exception:
                pass
            else:
                break

    def tearDown(self):
        call_command('clear_neo_db')

    def test_flag_comment_view_correct_data_spam(self):
        my_dict = {'current_user': self.user.email,
                   'flag_reason': 'spam',
                   'comment_uuid': str(uuid1())}
        request = self.factory.post('/comments/flag_comment/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = flag_comment(request)

        self.assertEqual(response.status_code, 200)

    def test_flag_comment_view_correct_data_explicit(self):
        my_dict = {'current_user': self.user.email,
                   'flag_reason': 'explicit',
                   'comment_uuid': str(uuid1())}
        request = self.factory.post('/comments/flag_comment/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = flag_comment(request)

        self.assertEqual(response.status_code, 200)

    def test_flag_comment_view_correct_data_other(self):
        my_dict = {'current_user': self.user.email,
                   'flag_reason': 'other',
                   'comment_uuid': str(uuid1())}
        request = self.factory.post('/comments/flag_comment/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = flag_comment(request)

        self.assertEqual(response.status_code, 200)

    def test_flag_comment_view_missing_data(self):
        my_dict = {'current_user': self.user.email,
                   'flag_reason': 'spam'}
        request = self.factory.post('/comments/flag_comment/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = flag_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_flag_comment_view_int_data(self):
        my_dict = 98897965
        request = self.factory.post('/comments/flag_comment/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = flag_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_flag_comment_view_string_data(self):
        my_dict = 'sdfasdfasdf'
        request = self.factory.post('/comments/flag_comment/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = flag_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_flag_comment_view_list_data(self):
        my_dict = []
        request = self.factory.post('/comments/flag_comment/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = flag_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_flag_comment_view_float_data(self):
        my_dict = 1.010101010
        request = self.factory.post('/comments/flag_comment/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = flag_comment(request)

        self.assertEqual(response.status_code, 400)

    def test_flag_comment_view_image_data(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/comments/flag_comment/', data=image,
                                    format='json')
        request.user = self.user
        response = flag_comment(request)

        self.assertEqual(response.status_code, 400)