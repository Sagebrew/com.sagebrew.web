import time
from uuid import uuid1
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command

from plebs.neo_models import Pleb
from sb_relationships.tasks import create_friend_request_task
from sb_registration.utils import create_user_util

class TestCreateFriendRequestTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        while not res['task_id'].ready():
            time.sleep(1)
        self.assertTrue(res['task_id'].result)
        while True:
            try:
                self.pleb1 = Pleb.nodes.get(email=self.email)
                self.user1 = User.objects.get(email=self.email)
            except Exception:
                pass
            else:
                break
        self.email2= "bounce@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email2, "testpassword")
        while not res['task_id'].ready():
            time.sleep(1)
        self.assertTrue(res['task_id'].result)
        while True:
            try:
                self.pleb2 = Pleb.nodes.get(email=self.email2)
                self.user2 = User.objects.get(email=self.email2)
            except Exception:
                pass
            else:
                break
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        call_command('clear_neo_db')
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_friend_request_task_success(self):
        data = {'data':
                    {
                        'from_pleb': self.pleb1.email,
                        'to_pleb': self.pleb2.email,
                        'friend_request_uuid': str(uuid1())
                    }
        }
        res = create_friend_request_task.apply_async(kwargs=data)

        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(res)

    def test_create_friend_request_task_failure_pleb_does_not_exist(self):
        data = {'data':
                    {
                        'from_pleb': 'totallyfakepleb@gmail.com',
                        'to_pleb': self.pleb2.email,
                        'friend_request_uuid': str(uuid1())
                    }
        }
        res = create_friend_request_task.apply_async(kwargs=data)

        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertFalse(res)

