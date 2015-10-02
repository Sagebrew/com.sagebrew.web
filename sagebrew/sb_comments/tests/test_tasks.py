import time
from uuid import uuid1

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from neomodel import DoesNotExist

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_questions.neo_models import Question
from sb_notifications.neo_models import Notification

from sb_comments.neo_models import Comment
from sb_comments.tasks import spawn_comment_notifications


class TestSpawnCommentNotifications(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(title=str(uuid1())).save()
        self.comment = Comment().save()
        settings.CELERY_ALWAYS_EAGER = True
        self.email2 = "bounce@simulator.amazonses.com"
        create_user_util_test(self.email2)
        self.pleb2 = Pleb.nodes.get(email=self.email2)

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

    def test_spawn_comment_notifications_comment_on_comment(self):
        self.question.owned_by.connect(self.pleb)
        self.question.owner_username = self.pleb.username
        self.question.save()
        self.question.comments.connect(self.comment)
        self.comment.comment_on.connect(self.question)
        self.comment.owned_by.connect(self.pleb)
        comment = Comment(owner_username=self.pleb2.username).save()
        comment.owned_by.connect(self.pleb2)
        self.question.comments.connect(comment)
        comment.comment_on.connect(self.question)
        self.pleb2.comments.connect(comment)
        notification_id = str(uuid1())
        comment_on_comment_id = str(uuid1())
        data = {
            "object_uuid": self.comment.object_uuid,
            "parent_object_uuid": self.question.object_uuid,
            "from_pleb": self.pleb2.username,
            "notification_id": notification_id,
            "comment_on_comment_id": comment_on_comment_id
        }
        res = spawn_comment_notifications.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
