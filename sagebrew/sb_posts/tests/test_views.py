import time
import pytz
from datetime import datetime
from uuid import uuid1
from json import dumps, loads
from rest_framework.test import APIRequestFactory, APIClient
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory


from plebs.neo_models import Pleb
from sb_posts.neo_models import SBPost
from sb_posts.utils import save_post
from sb_posts.views import save_post_view, edit_post, delete_post

class SubmitPostTest(TestCase):

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


    def test_submit_post_without_profane_content(self):
        my_dict = {"content": "This is a clean post",
                   "current_pleb": self.user.email,
                   "wall_pleb": self.user.email}
        request = self.factory.post('/posts/submit_post/', data=my_dict)
        request.user = self.user
        response = save_post_view(request)

        self.assertEqual(response.status_code, 200)
        time.sleep(1)

    def test_submit_post_with_profane_content(self):
        my_dict = {"content": "Fuck Shit Dicks Cock Niggers Spic Ass Cunt Fag",
                   "current_pleb": "tyler.wiersing@gmail.com",
                   "wall_pleb": "tyler.wiersing@gmail.com"}
        request = self.factory.post('/posts/submit_post/', data=my_dict)
        request.user = self.user
        response = save_post_view(request)

        self.assertEqual(response.status_code, 200)
        time.sleep(1)

class EditPostTests(TestCase):

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

    def test_same_content(self):
        my_dict = {
            "post_uuid": str(uuid1()),
            "content": "test edit post same content",
            "current_pleb": "tyler.wiersing@gmail.com",
            "wall_pleb": "tyler.wiersing@gmail.com"
        }
        my_post = save_post(**my_dict)
        my_edit_dict = {
            'content': 'test edit post same content',
            'post_uuid': my_post.post_id,
            'current_pleb': self.user.email,
        }
        request = self.factory.post('/posts/edit_post/', data=my_edit_dict,format='json')
        request.user = self.user
        response = edit_post(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], 'Cannot edit: content is the same')

    def test_to_be_deleted(self):
        my_dict = {
            "post_uuid": str(uuid1()),
            "content": "test edit post same content",
            "current_pleb": "tyler.wiersing@gmail.com",
            "wall_pleb": "tyler.wiersing@gmail.com"
        }
        my_post = save_post(**my_dict)
        my_post.to_be_deleted = True
        my_post.save()
        my_edit_dict = {
            'content': 'test edit post',
            'post_uuid': my_post.post_id,
            'current_pleb': self.user.email,
        }
        request = self.factory.post('/posts/edit_post/', data=my_edit_dict,format='json')
        request.user = self.user
        response = edit_post(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], 'Cannot edit: to be deleted')

    def test_same_timestamp(self):
        edit_time = datetime.now()
        my_dict = {
            "post_uuid": str(uuid1()),
            "content": "test edit post same content",
            "current_pleb": "tyler.wiersing@gmail.com",
            "wall_pleb": "tyler.wiersing@gmail.com"
        }
        my_post = save_post(**my_dict)
        my_post.last_edited_on = edit_time
        my_post.save()
        my_edit_dict = {
            'content': 'test edit post',
            'post_uuid': my_post.post_id,
            'current_pleb': self.user.email,
            'last_edited_on': edit_time
        }
        print 'same timestamp'
        request = self.factory.post('/posts/edit_post/', data=my_edit_dict,format='json')
        request.user = self.user
        response = edit_post(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], 'Cannot edit: time stamp is the same')

    def test_keep_recent_post(self):
        edit_time = datetime.now()
        my_dict = {
            "post_uuid": str(uuid1()),
            "content": "test edit post same content",
            "current_pleb": "tyler.wiersing@gmail.com",
            "wall_pleb": "tyler.wiersing@gmail.com"
        }
        my_post = save_post(**my_dict)
        my_post.last_edited_on = datetime.now()
        my_post.save()
        my_edit_dict = {
            'content': 'test edit post',
            'post_uuid': my_post.post_id,
            'current_pleb': self.user.email,
            'last_edited_on': edit_time
        }
        print 'recent time stamp'
        request = self.factory.post('/posts/edit_post/', data=my_edit_dict, format='json')
        request.user = self.user
        response = edit_post(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], 'Cannot edit: last edit more recent')