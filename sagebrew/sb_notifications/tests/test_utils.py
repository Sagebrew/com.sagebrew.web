from uuid import uuid1

from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework.reverse import reverse

from sb_comments.neo_models import Comment
from sb_posts.neo_models import Post
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_notifications.utils import (create_notification_util,
                                    create_system_notification)
from sb_notifications.neo_models import Notification


class TestNotificationUtils(TestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.email2 = "bounce@simulator.amazonses.com"
        create_user_util_test(self.email2)
        self.pleb2 = Pleb.nodes.get(email=self.email2)
        self.user2 = User.objects.get(email=self.email2)
        self.url = "http://localhost.com"

    def test_create_post_notification(self):
        post = Post(object_uuid=uuid1(), content='as;ldkfja;')
        post.save()

        response = create_notification_util(post.object_uuid, self.pleb,
                                            [self.pleb2],
                                            str(uuid1()), self.url,
                                            post.action_name)

        self.assertTrue(response)

    def test_create_post_notification_user_is_same(self):
        post = Post(content='as;ldkfja;')
        post.save()
        response = create_notification_util(post.object_uuid, self.pleb,
                                            [self.pleb],
                                            str(uuid1()), self.url,
                                            post.action_name)

        self.assertTrue(response)

    def test_create_post_notification_already_exists_sent(self):
        notification = Notification(sent=True).save()

        post = Post(object_uuid=uuid1(), content='as;ldkfja;')
        post.save()
        response = create_notification_util(post.object_uuid, self.pleb,
                                            [self.pleb2],
                                            notification.object_uuid, self.url,
                                            post.action_name)
        self.assertTrue(response)

    def test_create_post_notification_already_exists_not_sent(self):
        notification = Notification().save()
        post = Post(object_uuid=uuid1(), content='as;ldkfja;')
        post.save()
        response = create_notification_util(post.object_uuid, self.pleb,
                                            [self.pleb2],
                                            notification.object_uuid, self.url,
                                            post.action_name)

        self.assertTrue(response)

    def test_create_comment_notification(self):
        post = Post(content='as;ldkfja;')
        post.save()
        comment = Comment(content='sdfasd')
        comment.save()

        response = create_notification_util(comment.object_uuid, self.pleb,
                                            [self.pleb2],
                                            str(uuid1()), self.url,
                                            post.action_name)

        self.assertTrue(response)

    def test_create_comment_notification_pleb_is_the_same(self):
        post = Post(content='as;ldkfja;')
        post.save()
        comment = Comment(content='sdfasd')
        comment.save()

        response = create_notification_util(comment.object_uuid, self.pleb,
                                            [self.pleb],
                                            str(uuid1()), self.url,
                                            post.action_name)

        self.assertTrue(response)

    def test_create_comment_notification_already_exists_sent(self):
        comment = Comment(content='sdfasd')
        comment.save()
        notification = Notification(sent=True).save()
        post = Post(object_uuid=uuid1(), content='as;ldkfja;')
        post.save()
        response = create_notification_util(comment.object_uuid, self.pleb,
                                            [self.pleb2],
                                            notification.object_uuid, self.url,
                                            post.action_name)
        self.assertTrue(response)

    def test_create_comment_notification_already_exists_not_sent(self):
        comment = Comment(content='sdfasd')
        comment.save()
        notification = Notification().save()
        post = Post(content='as;ldkfja;')
        post.save()
        response = create_notification_util(comment.object_uuid, self.pleb,
                                            [self.pleb2],
                                            notification.object_uuid, self.url,
                                            post.action_name)
        self.assertTrue(response)

    def test_create_system_notification(self):
        notification_id = str(uuid1())
        res = create_system_notification(
            [self.pleb], notification_id,
            reverse('profile_page',
                    kwargs={"pleb_username": self.pleb.username}),
            "This is a test notification!")
        self.assertTrue(res)
        notification = Notification.nodes.get(object_uuid=notification_id)
        self.assertTrue(self.pleb in notification.notification_to)

    def test_create_system_notification_exists(self):
        notification = Notification().save()
        res = create_system_notification(
            [self.pleb], notification.object_uuid,
            reverse('profile_page',
                    kwargs={"pleb_username": self.pleb.username}),
            "This is a test notification!")
        self.assertTrue(res)
        notification = Notification.nodes.get(
            object_uuid=notification.object_uuid)
        self.assertTrue(self.pleb in notification.notification_to)
