from uuid import uuid1

from django.contrib.auth.models import User
from django.test import TestCase

from sb_comments.utils import save_comment_post
from sb_comments.neo_models import SBComment
from sb_notifications.utils import (create_notification_comment_util,
                                    create_notification_post_util)
from sb_posts.neo_models import SBPost
from plebs.neo_models import Pleb

class TestNotificationUtils(TestCase):
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
            username='Devon' + str(uuid1())[:25],
            email=str(uuid1())
        )
        self.pleb2 = Pleb.index.get(email=self.user2.email)

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

