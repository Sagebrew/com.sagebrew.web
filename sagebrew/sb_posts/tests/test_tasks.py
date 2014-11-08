import time
from uuid import uuid1
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import test_wait_util
from sb_posts.neo_models import SBPost
from sb_posts.tasks import (delete_post_and_comments, save_post_task)
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util


class TestSavePostTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_save_post_task(self):
        response = save_post_task.apply_async(kwargs=self.post_info_dict)
        while not response.ready():
            time.sleep(1)
        response = response.result
        self.assertTrue(response)


class TestDeletePostTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_delete_post_task(self):
        post = SBPost(content=self.post_info_dict['content'],
                      sb_id=self.post_info_dict['post_uuid'])
        post.save()
        delete_response = delete_post_and_comments.apply_async(
            [self.post_info_dict['post_uuid'], ])
        while not delete_response.ready():
            time.sleep(1)
        delete_response = delete_response.result
        self.assertTrue(delete_response)

class TestPostTaskRaceConditions(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}


class TestMultipleTasks(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}

    def test_create_many_posts(self):
        response_array = []
        for num in range(1, 10):
            uuid = str(uuid1())
            self.post_info_dict['post_uuid'] = uuid
            save_response = save_post_task.apply_async(
                kwargs=self.post_info_dict)
            while not save_response.ready():
                time.sleep(1)
            response_array.append(save_response.result)

        self.assertNotIn(False, response_array)
