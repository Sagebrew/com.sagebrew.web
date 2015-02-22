import time
from uuid import uuid1
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_relationships.tasks import create_friend_request_task
from sb_registration.utils import create_user_util_test

class TestCreateFriendRequestTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb1 = Pleb.nodes.get(email=self.email)
        self.user1 = User.objects.get(email=self.email)
        self.email2= "bounce@simulator.amazonses.com"
        res = create_user_util_test(self.email2)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb2 = Pleb.nodes.get(email=self.email2)
        self.user2 = User.objects.get(email=self.email2)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
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

        self.assertIsInstance(res, Exception)

    def test_create_friend_request_task_failure_missing_key(self):
        data = {'data':
                    {
                        'from_pleb': self.pleb1.email,
                        'to_pleb': self.pleb2.email
                    }
        }
        res = create_friend_request_task.apply_async(kwargs=data)

        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertIsInstance(res, Exception)


