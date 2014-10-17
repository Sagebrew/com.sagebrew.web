import time
from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command

from plebs.neo_models import Pleb
from sb_relationships.neo_models import FriendRequest
from sb_relationships.utils import create_friend_request_util
from sb_registration.utils import create_user_util

class TestCreateFriendRequestUtil(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        while not res['task_id'].ready():
            time.sleep(1)
        self.assertTrue(res['task_id'].result)
        while True:
            try:
                self.pleb1 = Pleb.nodes.get(email=self.email)
                self.user = User.objects.get(email=self.email)
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

    def tearDown(self):
        call_command('clear_neo_db')

    def test_create_friend_request_util_success(self):
        data = {'from_pleb': self.pleb1.email,
                'to_pleb': self.pleb2.email,
                'friend_request_uuid': str(uuid1())}
        res = create_friend_request_util(data)

        self.assertTrue(res)

    def test_create_friend_request_util_success_already_sent(self):
        friend_request = FriendRequest(friend_request_uuid=str(uuid1()))
        friend_request.save()
        self.pleb1.friend_requests_sent.connect(friend_request)
        self.pleb2.friend_requests_recieved.connect(friend_request)
        friend_request.request_to.connect(self.pleb2)
        friend_request.request_from.connect(self.pleb1)

        data = {'from_pleb': self.pleb1.email,
                'to_pleb': self.pleb2.email,
                'friend_request_uuid': str(uuid1())}
        res = create_friend_request_util(data)

        self.assertTrue(res)

    def test_create_friend_request_util_fail_pleb_does_not_exist(self):
        data = {'from_pleb': self.pleb1.email,
                'to_pleb': str(uuid1()),
                'friend_request_uuid': str(uuid1())}
        res = create_friend_request_util(data)

        self.assertEqual(res, None)

