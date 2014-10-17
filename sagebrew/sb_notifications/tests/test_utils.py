import time
from uuid import uuid1

from django.contrib.auth.models import User
from django.test import TestCase
from django.core.management import call_command

from sb_comments.neo_models import SBComment
from sb_notifications.utils import (create_notification_comment_util,
                                    create_notification_post_util)
from sb_posts.neo_models import SBPost
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util

class TestNotificationUtils(TestCase):
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

    def tearDown(self):
        call_command('clear_neo_db')

    def test_create_post_notification(self):
        post = SBPost(post_id=uuid1(), content='as;ldkfja;')
        post.save()

        response = create_notification_post_util(post.post_id,
                                                 self.pleb.email,
                                                 self.pleb2.email)

        self.assertTrue(response)

    def test_create_post_notification_post_does_not_exist(self):
        response = create_notification_post_util(str(uuid1()),
                                                 self.pleb.email,
                                                 self.pleb2.email)

        self.assertFalse(response)

    def test_create_post_notification_user_does_not_exist(self):
        post = SBPost(post_id=uuid1(), content='as;ldkfja;')
        post.save()
        response = create_notification_post_util(post.post_id,
                                                 self.pleb.email,
                                                 'fake email')

        self.assertFalse(response)

    def test_create_post_notification_user_is_same(self):
        post = SBPost(post_id=uuid1(), content='as;ldkfja;')
        post.save()
        response = create_notification_post_util(post.post_id,
                                                 self.pleb.email,
                                                 self.pleb.email)

        self.assertTrue(response)

    def test_create_comment_notification(self):
        post = SBPost(post_id=uuid1(), content='as;ldkfja;')
        post.save()
        comment = SBComment(comment_id=str(uuid1()), content='sdfasd')
        comment.save()

        response = create_notification_comment_util(self.pleb.email,
                                                    self.pleb2.email,
                                                    comment.comment_id,
                                                    'post',post.post_id)

        self.assertTrue(response)

    def test_create_comment_notification_comment_does_not_exist(self):
        post = SBPost(post_id=uuid1(), content='as;ldkfja;')
        post.save()

        response = create_notification_comment_util(self.pleb.email,
                                                    self.pleb2.email,
                                                    str(uuid1()),
                                                    'post',post.post_id)

        self.assertFalse(response)

    def test_create_comment_notification_pleb_does_not_exist(self):
        post = SBPost(post_id=uuid1(), content='as;ldkfja;')
        post.save()
        comment = SBComment(comment_id=str(uuid1()), content='sdfasd')
        comment.save()

        response = create_notification_comment_util('dfasdfasdf',
                                                    self.pleb2.email,
                                                    comment.comment_id,
                                                    'post',post.post_id)

        self.assertFalse(response)

    def test_create_comment_notification_pleb_is_the_same(self):
        post = SBPost(post_id=uuid1(), content='as;ldkfja;')
        post.save()
        comment = SBComment(comment_id=str(uuid1()), content='sdfasd')
        comment.save()

        response = create_notification_comment_util(self.pleb2.email,
                                                    self.pleb2.email,
                                                    comment.comment_id,
                                                    'post',post.post_id)

        self.assertTrue(response)

