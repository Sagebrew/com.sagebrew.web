import time
from uuid import uuid1
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command

from plebs.neo_models import Pleb
from sb_relationships.tasks import create_friend_request_task

class TestCreateFriendRequestTask(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        while True:
            try:
                self.pleb1 = Pleb.nodes.get(email=self.user1.email)
            except Exception:
                pass
            else:
                break
        self.user2 = User.objects.create_user(
            username='Tyler2', email=str(uuid1())+'@gmail.com')
        while True:
            try:
                self.pleb2 = Pleb.nodes.get(email=self.user2.email)
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

