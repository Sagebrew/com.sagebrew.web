import time

from uuid import uuid1
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_questions.neo_models import Question
from sb_questions.tasks import (add_auto_tags_to_question_task)


class TestAddAutoTagsToQuestionTask(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email, task=True)
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(object_uuid=str(uuid1()),
                                 content="This is some test content "
                                         "that I just created.",
                                 title=str(uuid1())).save()

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_add_auto_tags(self):
        data = {
            'object_uuid': self.question.object_uuid
        }
        res = add_auto_tags_to_question_task.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertNotIsInstance(res.result, Exception)

    def test_add_auto_tags_question_does_not_exist(self):
        data = {
            'object_uuid': str(uuid1())
        }
        res = add_auto_tags_to_question_task.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertIsInstance(res.result, Exception)
