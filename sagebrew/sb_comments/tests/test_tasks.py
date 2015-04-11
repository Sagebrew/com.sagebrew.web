import time
from uuid import uuid1
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from sb_comments.tasks import (create_comment_relations)
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_questions.neo_models import Question
from sb_comments.neo_models import Comment


class TestCreateCommentRelationsTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_comment_relations_task_success(self):
        question = Question(object_uuid=str(uuid1())).save()
        comment = Comment(object_uuid=str(uuid1())).save()
        task_data = {
            'current_pleb': self.pleb,
            'comment': comment,
            'sb_object': question
        }

        res = create_comment_relations.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)

