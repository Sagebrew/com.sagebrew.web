import pytz
import time
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User

from sb_notifications.tasks import (create_notification_post_task,
                                    create_notification_comment_task)
from sb_posts.neo_models import SBPost
from sb_comments.neo_models import SBComment
from plebs.neo_models import Pleb

class TestNotificationTasks(TestCase):
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
            username='Tyler' + str(uuid1())[:25], email=self.email)
        self.pleb = Pleb.index.get(email=self.email)
        self.user2 = User.objects.create_user(
            username='Devon' + str(uuid1())[:25], email='as;dflkjasd;')
        self.pleb2 = Pleb.index.get(email=self.user2.email)

        self.post_info_dict = {'content': 'test post',
                               'post_id': str(uuid1())}


    def test_create_notification_post_task(self):
        post = SBPost(**self.post_info_dict)
        post.save()

        data={'post_uuid': post.post_id, 'from_pleb': self.email,
              'to_pleb': self.pleb2.email}
        response = create_notification_post_task.apply_async(kwargs=data)

        self.assertTrue(response.get())

    def test_create_notification_post_task_post_fail(self):
        data={'post_uuid': str(uuid1()), 'from_pleb': self.email,
              'to_pleb': self.pleb2.email}
        response = create_notification_post_task.apply_async(kwargs=data)

        self.assertFalse(response.get())

    def test_create_notification_comment_task(self):
        post = SBPost(**self.post_info_dict)
        post.save()
        comment = SBComment(comment_id=str(uuid1()), content='sdfasd')
        comment.save()

        data = {'from_pleb':self.pleb.email, 'to_pleb': self.pleb2.email,
                'comment_on': 'post', 'comment_on_id': post.post_id,
                'comment_uuid': comment.comment_id}

        response = create_notification_comment_task.apply_async(kwargs=data)

        self.assertTrue(response.get())

    def test_create_notification_comment_task_fail(self):
        data = {'from_pleb':self.pleb.email, 'to_pleb': self.pleb2.email,
                'comment_on': 'post', 'comment_on_id': str(uuid1()),
                'comment_uuid': str(uuid1())}

        response = create_notification_comment_task.apply_async(kwargs=data)

        self.assertFalse(response.get())