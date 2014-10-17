import time
from json import loads
from uuid import uuid1
from base64 import b64encode
from rest_framework.test import APIRequestFactory
from django.core.management import call_command
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from plebs.neo_models import Pleb
from sb_relationships.neo_models import FriendRequest
from sb_relationships.views import (create_friend_request, get_friend_requests,
                                    respond_friend_request)
from sb_registration.utils import create_user_util

class TestCreateFriendRequestView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        while not res['task_id'].ready():
            time.sleep(1)
        self.assertTrue(res['task_id'].result)
        while True:
            try:
                self.pleb = Pleb.nodes.get(email=self.email)
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

    def test_create_friend_request_view_success(self):
        data = {
            'from_pleb': self.user.email,
            'to_pleb': self.user2.email,
            'friend_request_uuid': ''
        }
        request = self.factory.post('/relationships/create_friend_request',
                                    data=data, format='json')
        request.user = self.user

        res = create_friend_request(request)

        res.render()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(loads(res.content)['action'])

    def test_create_friend_request_view_invalid_form(self):
        data = {
            'from_pleb': self.user.email,
            'totallyincorrectform': self.user2.email,
            'friend_request_uuid': ''
        }
        request = self.factory.post('/relationships/create_friend_request',
                                    data=data, format='json')
        request.user = self.user

        res = create_friend_request(request)

        res.render()

        self.assertEqual(res.status_code, 400)
        self.assertEqual(loads(res.content)['detail'], 'invalid form')

    def test_create_friend_request_view_incorrect_data_int(self):
        request = self.factory.post('/relationships/create_friend_request',
                                    data=1123123, format='json')
        request.user = self.user

        res = create_friend_request(request)

        self.assertEqual(res.status_code, 400)

    def test_create_friend_request_view_incorrect_data_string(self):
        request = self.factory.post('/relationships/create_friend_request',
                                    data='1123123', format='json')
        request.user = self.user

        res = create_friend_request(request)

        self.assertEqual(res.status_code, 400)

    def test_create_friend_request_view_incorrect_data_float(self):
        request = self.factory.post('/relationships/create_friend_request',
                                    data=11.23123, format='json')
        request.user = self.user

        res = create_friend_request(request)

        self.assertEqual(res.status_code, 400)

    def test_create_friend_request_view_incorrect_data_list(self):
        request = self.factory.post('/relationships/create_friend_request',
                                    data=[], format='json')
        request.user = self.user

        res = create_friend_request(request)

        self.assertEqual(res.status_code, 400)

    def test_create_friend_request_view_incorrect_data_dict(self):
        request = self.factory.post('/relationships/create_friend_request',
                                    data={}, format='json')
        request.user = self.user

        res = create_friend_request(request)

        self.assertEqual(res.status_code, 400)

    def test_create_friend_request_view_incorrect_data_image(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/relationships/create_friend_request',
                                    data=image, format='json')
        request.user = self.user

        res = create_friend_request(request)

        self.assertEqual(res.status_code, 400)

class TestGetFriendRequestsView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        while not res['task_id'].ready():
            time.sleep(1)
        self.assertTrue(res['task_id'].result)
        while True:
            try:
                self.pleb = Pleb.nodes.get(email=self.email)
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

    def test_get_friend_request_view_success(self):
        data = {'email': self.user.email}
        request = self.factory.post('/relationships/query_friend_requests/',
                                    data=data, format='json')
        request.user = self.user

        res = get_friend_requests(request)

        self.assertEqual(res.status_code, 200)

    def test_get_friend_request_view_failure_invalid_form(self):
        data = {'fake': self.user.email}
        request = self.factory.post('/relationships/query_friend_requests/',
                                    data=data, format='json')
        request.user = self.user

        res = get_friend_requests(request)

        res.render()

        self.assertEqual(loads(res.content)['detail'], 'invalid form')
        self.assertEqual(res.status_code, 400)

    def test_get_friend_request_view_incorrect_data_int(self):
        request = self.factory.post('/relationships/query_friend_requests/',
                                    data=1312412, format='json')
        request.user = self.user

        res = get_friend_requests(request)

        self.assertEqual(res.status_code, 400)

    def test_get_friend_request_view_incorrect_data_string(self):
        request = self.factory.post('/relationships/query_friend_requests/',
                                    data='1312412', format='json')
        request.user = self.user

        res = get_friend_requests(request)

        self.assertEqual(res.status_code, 400)

    def test_get_friend_request_view_incorrect_data_float(self):
        request = self.factory.post('/relationships/query_friend_requests/',
                                    data=131.2412, format='json')
        request.user = self.user

        res = get_friend_requests(request)

        self.assertEqual(res.status_code, 400)

    def test_get_friend_request_view_incorrect_data_list(self):
        request = self.factory.post('/relationships/query_friend_requests/',
                                    data=[], format='json')
        request.user = self.user

        res = get_friend_requests(request)

        self.assertEqual(res.status_code, 400)

    def test_get_friend_request_view_incorrect_data_dict(self):
        request = self.factory.post('/relationships/query_friend_requests/',
                                    data={}, format='json')
        request.user = self.user

        res = get_friend_requests(request)

        self.assertEqual(res.status_code, 400)

    def test_get_friend_request_view_incorrect_data_image(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())
        request = self.factory.post('/relationships/query_friend_requests/',
                                    data=image, format='json')
        request.user = self.user

        res = get_friend_requests(request)

        self.assertEqual(res.status_code, 400)

class TestRespondFriendRequestView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        while not res['task_id'].ready():
            time.sleep(1)
        self.assertTrue(res['task_id'].result)
        while True:
            try:
                self.pleb = Pleb.nodes.get(email=self.email)
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

    def test_respond_friend_request_view_success_accept(self):
        friend_request = FriendRequest(friend_request_uuid=str(uuid1()))
        friend_request.save()
        pleb = Pleb.nodes.get(email=self.user.email)
        pleb2 = Pleb.nodes.get(email=self.user2.email)
        data = {
            'request_id': friend_request.friend_request_uuid,
            'response': 'accept'
        }
        friend_request.request_to.connect(pleb2)
        friend_request.request_from.connect(pleb)
        pleb.friend_requests_sent.connect(friend_request)
        pleb2.friend_requests_recieved.connect(friend_request)

        request = self.factory.post('/relationships/respond_friend_request/',
                                    data=data, format='json')

        request.user = self.user

        res = respond_friend_request(request)

        self.assertEqual(res.status_code, 200)

    def test_respond_friend_request_view_success_deny(self):
        friend_request = FriendRequest(friend_request_uuid=str(uuid1()))
        friend_request.save()
        pleb = Pleb.nodes.get(email=self.user.email)
        pleb2 = Pleb.nodes.get(email=self.user2.email)
        data = {
            'request_id': friend_request.friend_request_uuid,
            'response': 'deny'
        }
        friend_request.request_to.connect(pleb2)
        friend_request.request_from.connect(pleb)
        pleb.friend_requests_sent.connect(friend_request)
        pleb2.friend_requests_recieved.connect(friend_request)

        request = self.factory.post('/relationships/respond_friend_request/',
                                    data=data, format='json')

        request.user = self.user

        res = respond_friend_request(request)

        self.assertEqual(res.status_code, 200)

    def test_respond_friend_request_view_success_block(self):
        friend_request = FriendRequest(friend_request_uuid=str(uuid1()))
        friend_request.save()
        pleb = Pleb.nodes.get(email=self.user.email)
        pleb2 = Pleb.nodes.get(email=self.user2.email)
        data = {
            'request_id': friend_request.friend_request_uuid,
            'response': 'block'
        }
        friend_request.request_to.connect(pleb2)
        friend_request.request_from.connect(pleb)
        pleb.friend_requests_sent.connect(friend_request)
        pleb2.friend_requests_recieved.connect(friend_request)

        request = self.factory.post('/relationships/respond_friend_request/',
                                    data=data, format='json')

        request.user = self.user

        res = respond_friend_request(request)

        friend_request.refresh()

        self.assertEqual(friend_request.response, 'block')
        self.assertEqual(res.status_code, 200)

    def test_respond_friend_request_view_failure_invalid_form(self):
        data = {
            'rst_id': str(uuid1()),
            'response': 'accept'
        }

        request = self.factory.post('/relationships/respond_friend_request/',
                                    data=data, format='json')

        request.user = self.user

        res = respond_friend_request(request)
        res.render()

        self.assertEqual(loads(res.content)['detail'], 'invalid form')
        self.assertEqual(res.status_code, 400)

    def test_respond_friend_request_view_failure_incorrect_data_int(self):
        request = self.factory.post('/relationships/respond_friend_request/',
                                    data=1545, format='json')

        request.user = self.user

        res = respond_friend_request(request)

        self.assertEqual(res.status_code, 400)

    def test_respond_friend_request_view_failure_incorrect_data_string(self):
        request = self.factory.post('/relationships/respond_friend_request/',
                                    data='1545', format='json')

        request.user = self.user

        res = respond_friend_request(request)

        self.assertEqual(res.status_code, 400)

    def test_respond_friend_request_view_failure_incorrect_data_float(self):
        request = self.factory.post('/relationships/respond_friend_request/',
                                    data=15.45, format='json')

        request.user = self.user

        res = respond_friend_request(request)

        self.assertEqual(res.status_code, 400)

    def test_respond_friend_request_view_failure_incorrect_data_list(self):
        request = self.factory.post('/relationships/respond_friend_request/',
                                    data=[], format='json')

        request.user = self.user

        res = respond_friend_request(request)

        self.assertEqual(res.status_code, 400)

    def test_respond_friend_request_view_failure_incorrect_data_dict(self):
        request = self.factory.post('/relationships/respond_friend_request/',
                                    data={}, format='json')

        request.user = self.user

        res = respond_friend_request(request)

        self.assertEqual(res.status_code, 400)

    def test_respond_friend_request_view_failure_incorrect_data_image(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())
        request = self.factory.post('/relationships/respond_friend_request/',
                                    data=image, format='json')

        request.user = self.user

        res = respond_friend_request(request)

        self.assertEqual(res.status_code, 400)

