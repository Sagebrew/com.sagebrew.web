import time
import pytz
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_questions.neo_models import SBQuestion
from sb_registration.utils import create_user_util
from api.tasks import get_pleb_task

class TestGetPlebTask(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = SBQuestion(sb_id=str(uuid1()))
        self.question.save()

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_get_pleb_task(self):
        task_data = {
            'email': 'success@simulator.amazonses.com',
            'task_func': get_pleb_task,
            'task_param': {}
        }
        res = get_pleb_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)

    def test_get_pleb_task_pleb_does_not_exist(self):
        task_data = {
            'email': '11341@amazonses.com',
            'task_func': get_pleb_task,
            'task_param': {}
        }
        res = get_pleb_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)