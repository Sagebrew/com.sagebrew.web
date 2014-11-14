import time
from uuid import uuid1
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from plebs.neo_models import Pleb
from api.utils import test_wait_util
from sb_questions.neo_models import SBQuestion
from sb_registration.utils import create_user_util
from sb_flags.tasks import flag_object_task


class TestEditObjectTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_flag_object_task_success(self):
        question = SBQuestion(sb_id=str(uuid1())).save()
        task_data = {
            'current_pleb': self.pleb,
            'object_uuid': question.sb_id,
            'object_type': 'sb_questions.neo_models.SBQuestion',
            'flag_reason': 'spam',
            'description': ''
        }
        res = flag_object_task.apply_async(kwargs=task_data)

        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, SBQuestion)

    def test_flag_object_task_get_object_failure(self):
        question = SBQuestion(sb_id=str(uuid1())).save()
        task_data = {
            'current_pleb': self.pleb,
            'object_uuid': question.sb_id,
            'object_type': 'SBQuestion',
            'flag_reason': 'spam',
            'description': ''
        }
        res = flag_object_task.apply_async(kwargs=task_data)

        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, Exception)
