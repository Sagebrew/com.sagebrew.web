import time
from uuid import uuid1

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_questions.neo_models import Question

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
