import time
from uuid import uuid1
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from sb_notifications.tasks import (spawn_notifications)
from sb_posts.neo_models import Post
from sb_comments.neo_models import Comment
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test


class TestNotificationTasks(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.email2 = "bounce@simulator.amazonses.com"
        res = create_user_util_test(self.email2)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb2 = Pleb.nodes.get(email=self.email2)
        self.user2 = User.objects.get(email=self.email2)

        self.post_info_dict = {'content': 'test post',
                               'object_uuid': str(uuid1())}
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_notification_post_task(self):
        post = Post(**self.post_info_dict)
        post.save()

        data={'sb_object': post,
              'from_pleb': self.pleb.email,
              'to_plebs': [self.pleb2.email,]}
        response = spawn_notifications.apply_async(kwargs=data)
        while not response.ready():
            time.sleep(3)
        self.assertTrue(response.result)

    def test_create_notification_comment_task(self):
        post = Post(**self.post_info_dict)
        post.save()
        comment = Comment(object_uuid=str(uuid1()), content='sdfasd')
        comment.save()

        data = {'from_pleb':self.pleb.email, 'to_plebs': [self.pleb2.email,],
                'sb_object': comment}

        response = spawn_notifications.apply_async(kwargs=data)
        while not response.ready():
            time.sleep(3)
        self.assertTrue(response.result)

    def test_create_notification_task_failure(self):
        post = Post(**self.post_info_dict)
        post.save()

        data={'sb_object': post,
              'from_pleb': self.pleb.email,
              'to_plebs': [self.pleb2.email, 'fakeemail1@fake.com']}
        response = spawn_notifications.apply_async(kwargs=data)
        while not response.ready():
            time.sleep(1)

        self.assertIsInstance(response.result, Exception)
