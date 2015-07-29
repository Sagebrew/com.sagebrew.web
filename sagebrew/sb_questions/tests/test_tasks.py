from uuid import uuid1
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from plebs.neo_models import Pleb

from sb_questions.neo_models import Question
from sb_registration.utils import create_user_util_test


class TestAddQuestionToIndicesTask(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(object_uuid=str(uuid1()))
        self.question.save()

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False