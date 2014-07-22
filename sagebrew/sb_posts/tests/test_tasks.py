import pytz
import time
from uuid import uuid1
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from sb_posts.utils import save_post, edit_post_info, delete_post_info
from sb_posts.tasks import (delete_post_and_comments, save_post_task, edit_post_info_task,
                            create_downvote_post, create_upvote_post)
from sb_posts.neo_models import SBPost
from plebs.neo_models import Pleb

class TestPostTasks(TestCase):

    def setUp(self):
        self.email = 'devon@sagebrew.com'
        try:
            pleb = Pleb.index.get(email=self.email)
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
        except Pleb.DoesNotExist:
            pass

        self.user = User.objects.create_user(
            username='Tyler'+str(uuid1())[:25], email=self.email)
        self.pleb = Pleb.index.get(email=self.email)

        self.post_info_dict = {'current_pleb': self.pleb.email,
                          'wall_pleb': self.pleb.email,
                          'content': 'test post',
                          'post_id': str(uuid1())}

    def test_save_post_task(self):
        response = save_post_task.apply_async([self.post_info_dict,])

        self.assertEqual(response.get(), True)

    def test_delete_post_task(self):
        response = save_post_task.apply_async([self.post_info_dict,])
        delete_response = delete_post_and_comments.apply_async([self.post_info_dict['post_id'],])

        self.assertEqual(response.get(), True)
        self.assertEqual(delete_response.get(), True)

    def test_edit_post_task(self):
        edit_post_dict = {'content': 'Post edited',
                          'post_id': self.post_info_dict['post_id']}
        response = save_post_task.apply_async([self.post_info_dict,])
        edit_response = edit_post_info_task.apply_async([edit_post_dict,])

        self.assertEqual(response.get(), True)
        self.assertEqual(edit_response.get(), True)

    def test_edit_delete_post_tasks(self):
        edit_post_dict = {'content': 'Post edited',
                          'post_id': self.post_info_dict['post_id']}
        response = save_post_task.apply_async([self.post_info_dict,])
        edit_response = edit_post_info_task.apply_async([edit_post_dict,])
        delete_response = delete_post_and_comments.apply_async([self.post_info_dict['post_id'],])

        self.assertEqual(response.get(), True)
        self.assertEqual(edit_response.get(), True)
        self.assertEqual(delete_response.get(), True)

class TestMultipleTasks(TestCase):

    def setUp(self):
        self.email = 'devon@sagebrew.com'
        try:
            pleb = Pleb.index.get(email=self.email)
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
        except Pleb.DoesNotExist:
            pass

        self.user = User.objects.create_user(
            username='Tyler'+str(uuid1())[:25], email=self.email)
        self.pleb = Pleb.index.get(email=self.email)

        self.post_info_dict = {'current_pleb': self.pleb.email,
                          'wall_pleb': self.pleb.email,
                          'content': 'test post',
                          'post_id': str(uuid1())}

    def test_create_many_posts(self):
        response_array = []
        for num in range(1,10):
            uuid=str(uuid1())
            self.post_info_dict['post_id'] = uuid

            response = save_post_task.apply_async([self.post_info_dict,])
            response_array.append(response)
            time.sleep(1)

        for item in response_array:
            self.assertEqual(item.get(), True)