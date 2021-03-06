import time
import requests_mock
from uuid import uuid1

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework import status

from sb_registration.utils import create_user_util_test
from sb_questions.neo_models import Question
from sb_notifications.neo_models import Notification

from sb_comments.neo_models import Comment
from sb_comments.tasks import spawn_comment_notifications


class TestSpawnCommentNotifications(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.api_endpoint = "http://testserver/v1"
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(title=str(uuid1())).save()
        self.comment = Comment(
            owner_username=self.pleb.username,
            url="%s/questions/%s/" %
                (self.api_endpoint, self.question.object_uuid)).save()
        self.email2 = "bounce@simulator.amazonses.com"
        self.pleb2 = create_user_util_test(self.email2)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_spawn_comment_notifications(self):
        data = {
            "object_uuid": self.comment.object_uuid,
            "parent_object_uuid": self.question.object_uuid,
            "from_pleb": self.pleb.username,
            "notification_id": str(uuid1())
        }
        res = spawn_comment_notifications.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)

    def test_spawn_comment_notification_comment_does_not_exist(self):
        data = {
            "object_uuid": str(uuid1()),
            "parent_object_uuid": self.question.object_uuid,
            "from_pleb": self.pleb.username,
            "notification_id": str(uuid1())
        }
        res = spawn_comment_notifications.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertIsInstance(res.result, Exception)

    @requests_mock.mock()
    def test_spawn_comment_notifications_comment_on_comment(self, m):
        m.get("%s/questions/%s/" % (self.api_endpoint,
                                    self.question.object_uuid),
              json={
                  "url": "http://www.sagebrew.com/v1/questions/%s/" %
                         self.question.object_uuid},
              status_code=status.HTTP_200_OK)
        comment2 = Comment(owner_username=self.pleb2.username,
                           url="%s/questions/%s/" %
                               (self.api_endpoint,
                                self.question.object_uuid)).save()
        comment = Comment(owner_username=self.pleb.username,
                          url="%s/questions/%s/" %
                              (self.api_endpoint,
                               self.question.object_uuid)).save()
        self.question.owned_by.connect(self.pleb)
        self.question.owner_username = self.pleb.username
        self.question.save()

        comment.owned_by.connect(self.pleb)
        self.question.comments.connect(comment)

        comment2.owned_by.connect(self.pleb2)
        self.question.comments.connect(comment2)

        notification_id = str(uuid1())
        comment_on_comment_id = str(uuid1())
        data = {
            "object_uuid": comment.object_uuid,
            "parent_object_uuid": self.question.object_uuid,
            "from_pleb": self.pleb.username,
            "notification_id": notification_id,
            "comment_on_comment_id": comment_on_comment_id
        }
        res = spawn_comment_notifications.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
        while not res.result['comment_on_comment_task'].ready():
            time.sleep(1)
        notification = Notification.nodes.get(
            object_uuid=comment_on_comment_id)
        self.assertEqual(notification.action_name, "commented on a question "
                                                   "you commented on")
        self.assertTrue(self.pleb2 in notification.notification_to)
