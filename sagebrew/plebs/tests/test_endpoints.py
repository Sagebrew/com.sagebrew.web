from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from api.utils import wait_util
from plebs.neo_models import Pleb, FriendRequest
from sb_registration.utils import create_user_util_test


class MeEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"

    def test_unauthorized(self):
        url = reverse('me-detail')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        data = {'this': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        data = {}
        response = self.client.post(url, data=data, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        data = None
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_username(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.get(url, format='json')
        self.assertEqual('test_test', response.data['username'])

    def test_get_first_name(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.get(url, format='json')
        self.assertEqual('test', response.data['first_name'])

    def test_get_last_name(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.get(url, format='json')
        self.assertEqual('test', response.data['last_name'])

    def test_get_profile_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.get(url, format='json')
        self.assertIsNone(response.data['profile_pic'])

    def test_get_wallpaper_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.get(url, format='json')
        self.assertIsNone(response.data['profile_pic'])

    def test_get_url(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.get(url, format='json')
        self.assertEqual('http://testserver/user/test_test/',
                         response.data['url'])

    def test_get_privileges(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.get(url, format='json')
        self.assertEqual([], response.data['privileges'])

    def test_get_actions(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.get(url, format='json')
        self.assertEqual([], response.data['actions'])

    def test_get_href(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.get(url, format='json')
        self.assertEqual("http://testserver/v1/profiles/test_test/",
                         response.data['href'])

    def test_get_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.get(url, format='json')
        self.assertEqual("profile", response.data['type'])

    def test_get_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.get(url, format='json')
        self.assertEqual("test_test", response.data['id'])

    def test_get_reputation(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.get(url, format='json')
        self.assertEqual(0, response.data['reputation'])


class FriendRequestEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'friend_requests'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.friend_request = FriendRequest().save()
        self.pleb.friend_requests_received.connect(self.friend_request)
        self.pleb.friend_requests_sent.connect(self.friend_request)
        self.friend_request.request_to.connect(self.pleb)
        self.friend_request.request_from.connect(self.pleb)

    def test_list_unauthorized(self):
        url = reverse('friend_request-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_get_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_unauthorized(self):
        url = reverse('friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_get_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({
            "id": response.data['id'],
            "type": "friend_request",
            "seen": False,
            "time_sent": response.data['time_sent'],
            "time_seen": None,
            "response": None,
            "from_user": response.data['from_user'],
            "to_user": response.data['to_user']
        }, response.data)
        self.assertIn('http', response.data['from_user'])
        self.assertIn('http', response.data['to_user'])

    def test_update_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.put(url, data={'seen': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_incorrect_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.put(url, data={'fake_key': 'fake value'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
