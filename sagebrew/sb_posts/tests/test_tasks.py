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
        save_response = save_post_task.apply_async([self.post_info_dict,])
        delete_response = delete_post_and_comments.apply_async([self.post_info_dict['post_id'],])
        while not delete_response.ready():
            time.sleep(1)
        delete_response = delete_response.result
        while True:
            if delete_response == True:
                break
            else:
                response = delete_post_and_comments.AsyncResult(delete_response)
                while not response.ready():
                    time.sleep(1)
                delete_response = response.result

        self.assertTrue(save_response.get())
        self.assertTrue(delete_response)

    def test_edit_post_task(self):
        edit_post_dict = {'content': 'Post edited',
                          'post_id': self.post_info_dict['post_id']}
        save_response = save_post_task.apply_async([self.post_info_dict,])
        edit_response = edit_post_info_task.apply_async([edit_post_dict,])

        while not edit_response.ready():
            time.sleep(1)
        edit_response = edit_response.result
        while True:
            if edit_response == True:
                break
            else:
                response = edit_post_info_task.AsyncResult(edit_response)
                while not response.ready():
                    time.sleep(1)
                edit_response = response.result

        self.assertTrue(save_response.get())
        self.assertTrue(edit_response)

    def test_edit_delete_post_tasks(self):
        edit_post_dict = {'content': 'Post edited',
                          'post_id': self.post_info_dict['post_id']}
        response = save_post_task.apply_async([self.post_info_dict,])
        edit_response = edit_post_info_task.apply_async([edit_post_dict,])
        delete_response = delete_post_and_comments.apply_async([self.post_info_dict['post_id'],])

        self.assertTrue(response.get())
        self.assertTrue(edit_response.get())
        self.assertTrue(delete_response.get())

class TestTaskRaceConditions(TestCase):

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

    def test_race_condition_edit_multiple_times(self):
        edit_array = []
        response = save_post_task.apply_async([self.post_info_dict,])
        time.sleep(1)
        edit_dict = {'content': "post edited",
                     'post_id': self.post_info_dict['post_id']}
        for num in range(1,10):
            edit_response = edit_post_info_task.apply_async([edit_dict,])
            edit_array.append(edit_response)

        self.assertEqual(response.get(), True)
        for response in edit_array:
            self.assertTrue(response.get())

    def test_race_condition_create_same_post_twice(self):
        post_info_dict = {'current_pleb': self.pleb.email,
                          'wall_pleb': self.pleb.email,
                          'content': 'test post',
                          'post_id': 'create_two_posts_same_id'}
        response1 = save_post_task.apply_async([post_info_dict,])
        time.sleep(1)
        response2 = save_post_task.apply_async([post_info_dict,])

        self.assertTrue(response1.get())
        self.assertFalse(response2.get())

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