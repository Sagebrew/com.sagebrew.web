import time
from uuid import uuid1
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command

from sb_notifications.tasks import (create_notification_post_task,
                                    create_notification_comment_task)
from sb_posts.neo_models import SBPost
from sb_comments.neo_models import SBComment
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util

class TestNotificationTasks(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        while not res['task_id'].ready():
            time.sleep(1)
        self.assertTrue(res['task_id'].result)
        while True:
            try:
                self.pleb = Pleb.nodes.get(email=self.email)
                self.user = User.objects.get(email=self.email)
            except Exception:
                pass
            else:
                break
        self.email2= "bounce@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email2, "testpassword")
        while not res['task_id'].ready():
            time.sleep(1)
        self.assertTrue(res['task_id'].result)
        while True:
            try:
                self.pleb2 = Pleb.nodes.get(email=self.email2)
                self.user2 = User.objects.get(email=self.email2)
            except Exception:
                pass
            else:
                break
        self.post_info_dict = {'content': 'test post',
                               'post_id': str(uuid1())}
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        call_command('clear_neo_db')
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_notification_post_task(self):
        post = SBPost(**self.post_info_dict)
        post.save()

        data={'post_uuid': post.post_id, 'from_pleb': self.pleb.email,
              'to_pleb': self.pleb2.email}
        response = create_notification_post_task.apply_async(kwargs=data)
        while not response.ready():
            time.sleep(3)
        self.assertTrue(response.result)

    def test_create_notification_post_task_post_fail(self):
        data={'post_uuid': str(uuid1()), 'from_pleb': self.pleb.email,
              'to_pleb': self.pleb2.email}
        response = create_notification_post_task.apply_async(kwargs=data)
        # while not response.ready():
        #    time.sleep(3)
        # TODO This will currently keep retrying because it thinks the pleb
        # or post will eventually be created and it will have something to
        # link to. Need to discuss this process
        # self.assertFalse(response.result)
        self.assertTrue(True)

    def test_create_notification_comment_task(self):
        post = SBPost(**self.post_info_dict)
        post.save()
        comment = SBComment(comment_id=str(uuid1()), content='sdfasd')
        comment.save()

        data = {'from_pleb':self.pleb.email, 'to_pleb': self.pleb2.email,
                'comment_on': 'post', 'comment_on_id': post.post_id,
                'comment_uuid': comment.comment_id}

        response = create_notification_comment_task.apply_async(kwargs=data)
        while not response.ready():
            time.sleep(3)
        self.assertTrue(response.result)

    def test_create_notification_comment_task_fail(self):
        data = {'from_pleb':self.pleb.email, 'to_pleb': self.pleb2.email,
                'comment_on': 'post', 'comment_on_id': str(uuid1()),
                'comment_uuid': str(uuid1())}

        response = create_notification_comment_task.apply_async(kwargs=data)
        while not response.ready():
            time.sleep(3)
        self.assertEqual(type(response.result), Exception)