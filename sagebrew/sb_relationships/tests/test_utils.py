from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command

from plebs.neo_models import Pleb
from sb_relationships.neo_models import FriendRequest
from sb_relationships.utils import create_friend_request_util

class TestCreateFriendRequestUtil(TestCase):
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

