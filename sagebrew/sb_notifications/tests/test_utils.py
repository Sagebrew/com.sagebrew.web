import time
from uuid import uuid1

from django.contrib.auth.models import User
from django.test import TestCase
from django.core.management import call_command

from sb_comments.neo_models import SBComment
from sb_posts.neo_models import SBPost
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util
from sb_notifications.utils import create_notification_util
from sb_notifications.neo_models import NotificationBase

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

        response = create_notification_util(post, 'post', self.pleb,
                                            [self.pleb2], str(uuid1()))

        self.assertTrue(response['detail'])


    def test_create_post_notification_user_is_same(self):
        post = SBPost(post_id=uuid1(), content='as;ldkfja;')
        post.save()
        response = create_notification_util(post, 'post', self.pleb,
                                            [self.pleb], str(uuid1()))

        self.assertTrue(response['detail'])

    def test_create_post_notification_already_exists_sent(self):
        notification = NotificationBase(notification_uuid=str(uuid1()),
                                        sent=True).save()
        post = SBPost(post_id=uuid1(), content='as;ldkfja;')
        post.save()
        response = create_notification_util(post, 'post', self.pleb,
                                            [self.pleb2],
                                            notification.notification_id)
        self.assertTrue(response['detail'])

    def test_create_post_notification_already_exists_not_sent(self):
        notification = NotificationBase(notification_uuid=str(uuid1())).save()
        post = SBPost(post_id=uuid1(), content='as;ldkfja;')
        post.save()
        response = create_notification_util(post, 'post', self.pleb,
                                            [self.pleb2],
                                            notification.notification_id)

        self.assertTrue(response['detail'])

    def test_create_comment_notification(self):
        post = SBPost(post_id=uuid1(), content='as;ldkfja;')
        post.save()
        comment = SBComment(comment_id=str(uuid1()), content='sdfasd')
        comment.save()

        response = create_notification_util(comment, 'comment', self.pleb,
                                            [self.pleb2], str(uuid1()))

        self.assertTrue(response['detail'])

    def test_create_comment_notification_pleb_is_the_same(self):
        post = SBPost(post_id=uuid1(), content='as;ldkfja;')
        post.save()
        comment = SBComment(comment_id=str(uuid1()), content='sdfasd')
        comment.save()

        response = create_notification_util(comment, 'comment', self.pleb,
                                            [self.pleb], str(uuid1()))

        self.assertTrue(response['detail'])

    def test_create_comment_notification_already_exists_sent(self):
        comment = SBComment(comment_id=str(uuid1()), content='sdfasd')
        comment.save()
        notification = NotificationBase(notification_uuid=str(uuid1()),
                                        sent=True).save()
        post = SBPost(post_id=uuid1(), content='as;ldkfja;')
        post.save()
        response = create_notification_util(comment, 'comment', self.pleb,
                                            [self.pleb2],
                                            notification.notification_id)
        self.assertTrue(response['detail'])

    def test_create_comment_notification_already_exists_not_sent(self):
        comment = SBComment(comment_id=str(uuid1()), content='sdfasd')
        comment.save()
        notification = NotificationBase(notification_uuid=str(uuid1())).save()
        post = SBPost(post_id=uuid1(), content='as;ldkfja;')
        post.save()
        response = create_notification_util(comment, 'comment', self.pleb,
                                            [self.pleb2],
                                            notification.notification_id)
        self.assertTrue(response['detail'])