from uuid import uuid1

from django.contrib.auth.models import User
from django.test import TestCase

from api.utils import test_wait_util
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
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.email2= "bounce@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email2, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb2 = Pleb.nodes.get(email=self.email2)
        self.user2 = User.objects.get(email=self.email2)

    def test_create_post_notification(self):
        post = SBPost(sb_id=uuid1(), content='as;ldkfja;')
        post.save()

        response = create_notification_util(post, self.pleb, [self.pleb2],
                                            str(uuid1()))

        self.assertTrue(response)


    def test_create_post_notification_user_is_same(self):
        post = SBPost(sb_id=uuid1(), content='as;ldkfja;')
        post.save()
        response = create_notification_util(post, self.pleb, [self.pleb],
                                            str(uuid1()))

        self.assertTrue(response)

    def test_create_post_notification_already_exists_sent(self):
        notification = NotificationBase(notification_uuid=str(uuid1()),
                                        sent=True).save()
        post = SBPost(sb_id=uuid1(), content='as;ldkfja;')
        post.save()
        response = create_notification_util(post, self.pleb, [self.pleb2],
                                            notification.notification_uuid)
        self.assertTrue(response)

    def test_create_post_notification_already_exists_not_sent(self):
        notification = NotificationBase(notification_uuid=str(uuid1())).save()
        post = SBPost(sb_id=uuid1(), content='as;ldkfja;')
        post.save()
        response = create_notification_util(post, self.pleb, [self.pleb2],
                                            notification.notification_uuid)

        self.assertTrue(response)

    def test_create_comment_notification(self):
        post = SBPost(sb_id=uuid1(), content='as;ldkfja;')
        post.save()
        comment = SBComment(sb_id=str(uuid1()), content='sdfasd')
        comment.save()

        response = create_notification_util(comment, self.pleb, [self.pleb2],
                                            str(uuid1()))

        self.assertTrue(response)

    def test_create_comment_notification_pleb_is_the_same(self):
        post = SBPost(sb_id=uuid1(), content='as;ldkfja;')
        post.save()
        comment = SBComment(commesb_iduuid1()), content='sdfasd')
        comment.save()

        response = create_notification_util(comment, self.pleb, [self.pleb],
                                            str(uuid1()))

        self.assertTrue(response)

    def test_create_comment_notification_already_exists_sent(self):
        comment = SBComment(comment_idsb_id()), content='sdfasd')
        comment.save()
        notification = NotificationBase(notification_uuid=str(uuid1()),
                                        sent=True).save()
        post = SBPost(sb_id=uuid1(), content='as;ldkfja;')
        post.save()
        response = create_notification_util(comment, self.pleb, [self.pleb2],
                                            notification.notification_uuid)
        self.assertTrue(response)

    def test_create_comment_notification_already_exists_not_sent(self):
        comment = SBComment(comment_id=str(uuid1()), content='sdfasd')
        comment.save()
        notification = NotificationBase(notification_uuid=str(uuid1())).save()
        post = SBPost(sb_id=uuid1(), content='as;ldkfja;')
        post.save()
        response = create_notification_util(comment, self.pleb, [self.pleb2],
                                            notification.notification_uuid)
        self.assertTrue(response)
