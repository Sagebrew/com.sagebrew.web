import time
from uuid import uuid1
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util


class TestClearNeoDBCommand(TestCase):

    def test_clear_neo_db(self):
        email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", email, "testpassword")
        self.assertIsNotNone(res, "Issue Connecting to Celery Broker")

        while not res['task_id'].ready():
            time.sleep(1)
        self.assertTrue(res['task_id'].result)
        pleb = Pleb.nodes.get(email= email)
        user = User.objects.get(email=email)
        self.assertEqual(pleb.email, user.email)
        call_command("clear_neo_db")
        pleb = None
        try:
            pleb = Pleb.nodes.get(email=email)
            self.assertIsNone(pleb)
        except Pleb.DoesNotExist:
            self.assertIsNone(pleb)
