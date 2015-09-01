import time
from uuid import uuid1
import shortuuid
from collections import OrderedDict

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.cache import cache
from django.templatetags import static

from neomodel import db

from rest_framework import status
from rest_framework.test import APITestCase

from api.utils import wait_util
from sagebrew import errors
from sb_public_official.neo_models import PublicOfficial
from plebs.neo_models import Pleb, FriendRequest, Address, BetaUser
from sb_privileges.neo_models import Privilege, SBAction
from sb_campaigns.neo_models import Position, PoliticalCampaign
from sb_locations.neo_models import Location
from sb_questions.neo_models import Question
from sb_registration.utils import create_user_util_test
from sb_posts.neo_models import Post
from sb_solutions.neo_models import Solution
from sb_donations.neo_models import Donation


class MeEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"

    def test_unauthorized(self):
        url = reverse('me-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        data = {'this': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        data = {}
        response = self.client.post(url, data=data, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['detail'],
                         'Method "DELETE" not allowed.')

    def test_get_username(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual('test_test', response.data['username'])

    def test_get_first_name(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual('test', response.data['first_name'])

    def test_get_last_name(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual('test', response.data['last_name'])

    def test_get_profile_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['profile_pic'],
                         static.static("images/sage_coffee_grey-01.png"))

    def test_get_wallpaper_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['wallpaper_pic'],
                         static.static("images/wallpaper_western.jpg"))

    def test_get_url(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual('http://testserver/user/test_test/',
                         response.data['url'])

    def test_get_privileges(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual([], response.data['privileges'])

    def test_get_actions(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        cache.clear()
        response = self.client.get(url, format='json')
        self.assertEqual([], response.data['actions'])

    def test_get_actions_populated(self):
        self.client.force_authenticate(user=self.user)
        action = SBAction(resource="test_action").save()
        self.pleb.actions.connect(action)
        cache.clear()
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.pleb.actions.disconnect(action)
        self.assertEqual(['test_action'], response.data['actions'])

    def test_get_privileges_populated(self):
        self.client.force_authenticate(user=self.user)
        privilege = Privilege(name="test_privilege").save()
        self.pleb.privileges.connect(privilege)
        cache.clear()
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.pleb.privileges.disconnect(privilege)
        privilege.delete()
        self.assertEqual(['test_privilege'], response.data['privileges'])

    def test_get_href(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual("http://testserver/v1/profiles/test_test/",
                         response.data['href'])

    def test_get_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual("profile", response.data['type'])

    def test_get_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual("test_test", response.data['id'])

    def test_get_reputation(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        response = self.client.get(url, format='json')
        self.assertEqual(0, response.data['reputation'])

    def test_get_populated_wallpaper(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        wallpaper = self.pleb.wallpaper_pic
        self.pleb.wallpaper_pic = "http://helloworld.com/this.jpeg"
        self.pleb.save()
        cache.set(self.pleb.username, self.pleb)
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['wallpaper_pic'],
                         self.pleb.wallpaper_pic)
        self.pleb.wallpaper_pic = wallpaper
        self.pleb.save()

    def test_update(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-list')
        data = {
            "wallpaper_pic": "http://example.com/",
            "profile_pic": "http://example.com/"
        }
        res = self.client.put(url, data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_donations(self):
        donation = Donation().save()
        self.pleb.donations.connect(donation)
        donation.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-donations')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_donations_html(self):
        campaign = PoliticalCampaign(username='this is a test useranem').save()
        donation = Donation().save()
        self.pleb.donations.connect(donation)
        donation.owned_by.connect(self.pleb)
        donation.campaign.connect(campaign)
        campaign.donations.connect(donation)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-donations') + "?html=true"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class SentFriendRequestEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'friend_requests'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.email2 = "bounce@simulator.amazonses.com"
        create_user_util_test(self.email2)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb2 = Pleb.nodes.get(email=self.email2)
        self.url = "http://testserver"
        self.friend_request = FriendRequest().save()
        self.pleb.friend_requests_received.connect(self.friend_request)
        self.pleb.friend_requests_sent.connect(self.friend_request)
        self.friend_request.request_to.connect(self.pleb)
        self.friend_request.request_from.connect(self.pleb2)

    def test_list_unauthorized(self):
        url = reverse('sent_friend_request-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_get_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_unauthorized(self):
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_get_friend_request_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.friend_request.object_uuid)

    def test_get_friend_request_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], "friend_request")

    def test_get_friend_request_seen(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['seen'])

    def test_get_friend_request_time_sent(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['time_sent'],
                         self.friend_request.time_sent.isoformat()[:-6] + 'Z')

    def test_get_friend_request_time_seen(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['time_seen'],
                         self.friend_request.time_seen)

    def test_get_friend_request_response(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['response'])

    def test_get_friend_request_from_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['from_user'], dict)

    def test_get_friend_request_to_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['to_user'], dict)

    def test_get_friend_request_to_user_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_incorrect_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.put(url, data={'fake_key': 'fake value'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_friend_request_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-list')
        response = self.client.get(url)
        self.assertGreater(response.data['count'], 0)

    def test_get_friend_request_list_no_cache(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        url = reverse('sent_friend_request-list')
        response = self.client.get(url)
        self.assertGreater(response.data['count'], 0)

    def test_get_friend_request_list_cache(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('sent_friend_request-list')
        self.client.get(url)
        response = self.client.get(url)
        self.assertGreater(response.data['count'], 0)


class FriendManagerEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'friend'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.email2 = "bounce@simulator.amazonses.com"
        create_user_util_test(self.email2)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb2 = Pleb.nodes.get(email=self.email2)
        self.pleb.friends.connect(self.pleb2)
        self.pleb2.friends.connect(self.pleb)
        self.url = "http://testserver"

    def test_list_unauthorized(self):
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_detail_unauthorized(self):
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_get_friend_request_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.pleb2.username)

    def test_get_friend_request_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], "profile")

    def test_get_friend_request_profile_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertIsNone(response.data['profile_pic'])

    def test_get_friend_request_first_name(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.data['first_name'], 'test')

    def test_get_friend_request_last_name(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.data['last_name'], 'test')

    def test_get_friend_request_wallpaper_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertIsNone(response.data['wallpaper_pic'])

    def test_get_friend_request_url(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.data['url'], 'http://testserver/user'
                                               '/test_test1/')

    def test_get_friend_request_privileges(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.data['privileges'], [])

    def test_get_friend_request_actions(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.data['actions'], [])

    def test_get_friend_request_href(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.data['href'], 'http://testserver/'
                                                'v1/profiles/test_test1/')

    def test_get_friend_request_reputation(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.get(url)
        self.assertEqual(response.data['reputation'], 0)

    def test_get_friend_request_to_user_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend-detail',
                      kwargs={"friend_username": self.pleb2.username})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.pleb.friends.connect(self.pleb2)
        self.pleb2.friends.connect(self.pleb)


class ProfileEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_unauthorized(self):
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        data = {'this': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
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
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        data = {'detail': 'TBD'}
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)

    def test_get_username(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual('test_test', response.data['username'])

    def test_get_first_name(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual('test', response.data['first_name'])

    def test_get_last_name(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual('test', response.data['last_name'])

    def test_get_profile_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertIsNone(response.data['profile_pic'])

    def test_get_wallpaper_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertIsNone(response.data['profile_pic'])

    def test_get_url(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual('http://testserver/user/test_test/',
                         response.data['url'])

    def test_get_privileges(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual([], response.data['privileges'])

    def test_get_actions(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual([], response.data['actions'])

    def test_get_href(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual("http://testserver/v1/profiles/test_test/",
                         response.data['href'])

    def test_get_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual("profile", response.data['type'])

    def test_get_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual("test_test", response.data['id'])

    def test_get_reputation(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(0, response.data['reputation'])

    def test_get_pleb_no_cache(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', kwargs={
            'username': self.pleb.username})
        cache.clear()
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_pleb(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data, {'detail': 'TBD'})
        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)


class ProfileContentMethodTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_get_pleb_questions(self):
        question = Question(
            title="Hello there world",
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-questions', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertGreater(response.data['count'], 0)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_pleb_question_id(self):
        for item in Question.nodes.all():
            item.delete()
        question = Question(
            title="Hello there world",
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-questions', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['id'],
                         question.object_uuid)

    def test_get_pleb_question_type(self):
        for item in Question.nodes.all():
            item.delete()
        question = Question(
            title="Hello there world",
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-questions', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['type'],
                         'question')

    def test_get_pleb_question_object_uuid(self):
        for item in Question.nodes.all():
            item.delete()
        question = Question(
            title="Hello there world",
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-questions', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['object_uuid'],
                         question.object_uuid)

    def test_get_pleb_question_content(self):
        for item in Question.nodes.all():
            item.delete()
        question = Question(
            title="Hello there world",
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-questions', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['content'],
                         question.content)

    def test_get_pleb_question_profile(self):
        for item in Question.nodes.all():
            item.delete()
        question = Question(
            title="Hello there world",
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-questions', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['profile'],
                         "test_test")

    def test_get_pleb_question_url(self):
        for item in Question.nodes.all():
            item.delete()
        question = Question(
            title="Hello there world",
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-questions', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['url'],
                         "http://testserver/conversations/"
                         "%s/" % question.object_uuid)

    def test_get_pleb_question_title(self):
        for item in Question.nodes.all():
            item.delete()
        question = Question(
            title="Hello there world",
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-questions', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['title'],
                         "Hello there world")

    def test_get_pleb_question_invalid_query(self):
        self.client.force_authenticate(user=self.user)
        url = "%s?filter=error" % reverse('profile-questions', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data, errors.QUERY_DETERMINATION_EXCEPTION)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_pleb_question_public_content(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-public-content', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')

        self.assertGreater(response.data['count'], 0)

    def test_get_pleb_public_content_invalid_query(self):
        self.client.force_authenticate(user=self.user)
        url = "%s?filter=error" % reverse('profile-public-content', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data, errors.QUERY_DETERMINATION_EXCEPTION)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_pleb_public_content_id(self):
        for item in Question.nodes.all():
            item.delete()
        question = Question(
            title="Hello there world",
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-public-content', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['id'],
                         question.object_uuid)


class ProfileFriendsMethodTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_get_pleb_friends_type(self):
        friend = Pleb(username=shortuuid.uuid()).save()
        self.pleb.friends.connect(friend)
        friend.friends.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-friends', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['type'], 'profile')

    def test_get_pleb_friends_html(self):
        friend = Pleb(username=shortuuid.uuid()).save()
        self.pleb.friends.connect(friend)
        friend.friends.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse('profile-friends', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BaseUserTests(APITestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.email2 = "bounce@simulator.amazonses.com"
        create_user_util_test(self.email)
        create_user_util_test(self.email2)
        self.user = User.objects.get(email=self.email)
        self.unit_under_test = User.objects.get(email=self.email2)
        self.unit_under_test_name = "user"

    def test_unauthorized_message(self):
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data['detail'],
                         'Authentication credentials were not provided.')

    def test_unauthorized_status(self):
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_missing_data(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {'asset_uri': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_no_birthday(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})

        data = {"password": "hellothere2"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data['birthday'], ['This field is required.'])

    def test_update_no_email(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})

        data = {"password": "hellothere2"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data['email'], ['This field is required.'])

    def test_update_no_last_name(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})

        data = {"password": "hellothere2"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data['last_name'],
                         ['This field is required.'])

    def test_update_does_not_exist_status(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={"username": str(shortuuid.uuid())})
        data = {'status_code': status.HTTP_404_NOT_FOUND,
                'detail': 'Not found.'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_does_not_exist_message(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={"username": str(shortuuid.uuid())})
        data = {'status_code': status.HTTP_404_NOT_FOUND,
                'detail': 'Not found.'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data['detail'], 'Not found.')

    def test_update_bad_request(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})

        data = {"password": "hellothere2"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_list(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
                'detail': 'Method "PUT" not allowed.'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})
        data = None
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_list_detail(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['detail'],
                         'Method "DELETE" not allowed.')

    def test_delete_list_status(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_read_username(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})

        response = self.client.get(url, format='json')
        self.assertEqual(response.data['username'], 'test_test1')

    def test_read_profile(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})

        response = self.client.get(url, format='json')
        self.assertEqual(response.data['profile'],
                         'http://testserver/v1/profiles/test_test1/')

    def test_read_first_name(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['first_name'], 'test')

    def test_read_last_name(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['last_name'], 'test')

    def test_read_href(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['href'],
                         'http://testserver/v1/users/test_test1/')

    def test_read_type(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['type'], 'user')

    def test_read_id(self):
        self.client.force_authenticate(user=self.unit_under_test)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['id'], 'test_test1')

    def test_read_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, OrderedDict)

    def test_read_is_not_self(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_is_not_self_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})

        data = {"password": "hellothere2"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data['detail'],
                         'You do not have permission to perform this action.')

    def test_update_is_not_self_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'username': self.unit_under_test.username})

        data = {"password": "hellothere2"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class FriendRequestListTest(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'friend_request'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_unauthorized(self):
        url = reverse('friend_request-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-list')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-list')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-list')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-list')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-list')
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail_message(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-list')
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['detail'], 'Method "POST" not allowed.')

    def test_delete_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-list')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_message(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('notification-list')
        data = {}
        response = self.client.delete(url, data=data, format='json')
        self.assertEqual(response.data['detail'],
                         'Method "DELETE" not allowed.')

    def test_empty_list(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        for friend_request in self.pleb.friend_requests_received.all():
            friend_request.delete()
        url = reverse('friend_request-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'], 0)

    def test_list_with_items(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        friend_request = FriendRequest().save()
        friend_request.request_from.connect(self.pleb)
        friend_request.request_to.connect(self.pleb)
        self.pleb.friend_requests_received.connect(friend_request)
        url = reverse('friend_request-list')
        response = self.client.get(url, format='json')
        self.assertGreater(response.data['count'], 0)

    def test_list_seen_api(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        friend_request = FriendRequest().save()
        friend_request.request_from.connect(self.pleb)
        friend_request.request_to.connect(self.pleb)
        self.pleb.friend_requests_received.connect(friend_request)
        url = "%s?seen=true" % reverse('friend_request-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'], [])

    def test_list_seen_render(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        friend_request = FriendRequest().save()
        friend_request.request_from.connect(self.pleb)
        friend_request.request_to.connect(self.pleb)
        self.pleb.friend_requests_received.connect(friend_request)
        url = "%s?seen=true" % reverse('friend_request-render')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results']['unseen'], 0)

    def test_list_render_unseen(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        friend_request = FriendRequest().save()
        friend_request.request_from.connect(self.pleb)
        friend_request.request_to.connect(self.pleb)
        self.pleb.friend_requests_received.connect(friend_request)
        url = reverse('friend_request-render')
        response = self.client.get(url, format='json')
        self.assertGreater(response.data['results']['unseen'], 0)

    def test_list_render_ids(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        friend_request = FriendRequest().save()
        friend_request.request_from.connect(self.pleb)
        friend_request.request_to.connect(self.pleb)
        self.pleb.friend_requests_received.connect(friend_request)
        url = reverse('friend_request-render')
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data['results']['ids']), 0)

    def test_list_render_html(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        friend_request = FriendRequest().save()
        friend_request.request_from.connect(self.pleb)
        friend_request.request_to.connect(self.pleb)
        self.pleb.friend_requests_received.connect(friend_request)
        url = reverse('friend_request-render')
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data['results']['html']), 0)


class PlebSenatorsTest(APITestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.address = Address(street="3295 Rio Vista St",
                               city="Commerce Township", state="MI",
                               postal_code="48382", country="US",
                               congressional_district="11")
        self.address.save()
        self.address.owned_by.connect(self.pleb)
        self.pleb.address.connect(self.address)

    def test_unauthorized(self):
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail_message(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['detail'], 'Method "POST" not allowed.')

    def test_delete_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_message(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.delete(url, data=data, format='json')
        self.assertEqual(response.data['detail'],
                         'Method "DELETE" not allowed.')

    def test_empty_list(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        for senator in self.pleb.senators.all():
            self.pleb.senators.disconnect(senator)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual("<small>Sorry we could not find"
                         " your Senators. Please alert us to our "
                         "error!</small>", response.data)

    def test_list_senators(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        senator1 = PublicOfficial(first_name="Debbie", last_name="Stab",
                                  state="MI", bioguideid=shortuuid.uuid(),
                                  full_name="Debbie Stab [Dem]")
        senator1.save()
        senator2 = PublicOfficial(first_name="Tester", last_name="Test",
                                  state="MI", bioguideid=shortuuid.uuid())
        senator2.save()
        for senator in self.pleb.senators.all():
            self.pleb.senators.disconnect(senator)
        self.pleb.senators.connect(senator1)
        self.pleb.senators.connect(senator2)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data), 0)

    def test_list_senators_cache(self):
        senator1 = PublicOfficial(first_name="Debbie", last_name="Stab",
                                  state="MI", bioguideid=shortuuid.uuid(),
                                  full_name="Debbie Stab [Dem]")
        senator1.save()
        senator2 = PublicOfficial(first_name="Tester", last_name="Test",
                                  state="MI", bioguideid=shortuuid.uuid())
        senator2.save()
        for senator in self.pleb.senators.all():
            self.pleb.senators.disconnect(senator)
        self.pleb.senators.connect(senator1)
        self.pleb.senators.connect(senator2)
        self.client.force_authenticate(user=self.user)
        query = "MATCH (a:Pleb {username: '%s'})-[:HAS_SENATOR]->" \
                "(s:PublicOfficial) RETURN s" % self.user.username
        res, col = db.cypher_query(query)
        senators = [PublicOfficial.inflate(row[0]) for row in res]
        cache.set("%s_senators" % self.user.username, senators)
        url = reverse('profile-senators',
                      kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data), 0)

    def test_list_senators_html(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        senator1 = PublicOfficial(first_name="Debbie", last_name="Stab",
                                  state="MI", bioguideid=shortuuid.uuid(),
                                  full_name="Debbie Stab [Dem]")
        senator1.save()
        senator2 = PublicOfficial(first_name="Tester", last_name="Test",
                                  state="MI", bioguideid=shortuuid.uuid())
        senator2.save()
        for senator in self.pleb.senators.all():
            self.pleb.senators.disconnect(senator)
        self.pleb.senators.connect(senator1)
        self.pleb.senators.connect(senator2)
        url = "%s?html=true" % reverse('profile-senators',
                                       kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data), 0)


class PlebHouseRepresentativeTest(APITestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.address = Address(street="3295 Rio Vista St",
                               city="Commerce Township", state="MI",
                               postal_code="48382", country="US",
                               congressional_district="11")
        self.address.save()
        self.address.owned_by.connect(self.pleb)
        self.pleb.address.connect(self.address)

    def test_unauthorized(self):
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail_message(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data['detail'], 'Method "POST" not allowed.')

    def test_delete_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_message(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        data = {}
        response = self.client.delete(url, data=data, format='json')
        self.assertEqual(response.data['detail'],
                         'Method "DELETE" not allowed.')

    def test_empty_list(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        for senator in self.pleb.house_rep.all():
            self.pleb.house_rep.disconnect(senator)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual("<small>Sorry we could not find"
                         " your House Representative. Please alert us to our "
                         "error!</small>", response.data)

    def test_list_house_representative(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        house_representative = PublicOfficial(
            first_name="Debbie", last_name="Stab",
            state="MI", bioguideid=shortuuid.uuid(),
            full_name="Debbie Stab [Dem]",
            district=11)
        house_representative.save()
        for senator in self.pleb.house_rep.all():
            self.pleb.house_rep.disconnect(senator)
        self.pleb.house_rep.connect(house_representative)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data), 0)

    def test_list_house_representative_cache(self):
        house_representative = PublicOfficial(
            first_name="Debbie", last_name="Stab",
            state="MI", bioguideid=shortuuid.uuid(),
            full_name="Debbie Stab [Dem]",
            district=11)
        house_representative.save()
        for house_representative in self.pleb.house_rep.all():
            self.pleb.senators.disconnect(house_representative)
        self.pleb.house_rep.connect(house_representative)
        self.client.force_authenticate(user=self.user)
        query = "MATCH (a:Pleb {username: '%s'})-" \
                "[:HAS_HOUSE_REPRESENTATIVE]->" \
                "(s:PublicOfficial) RETURN s" % self.user.username
        res, col = db.cypher_query(query)
        senators = [PublicOfficial.inflate(row[0]) for row in res]
        cache.set("%s_senators" % self.user.username, senators)
        url = reverse('profile-house-representative',
                      kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data), 0)

    def test_list_house_representative_html(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        house_representative = PublicOfficial(
            first_name="Debbie", last_name="Stab",
            state="MI", bioguideid=shortuuid.uuid(),
            full_name="Debbie Stab [Dem]", district=11)
        house_representative.save()
        for house_rep in self.pleb.house_rep.all():
            self.pleb.house_rep.disconnect(house_rep)
        self.pleb.house_rep.connect(house_representative)
        url = "%s?html=true" % reverse('profile-house-representative',
                                       kwargs={'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertGreater(len(response.data), 0)


class AddressEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'address'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.address = Address(street="3295 Rio Vista St",
                               city="Commerce Township", state="MI",
                               postal_code="48382", country="US",
                               congressional_district="11")
        self.address.save()
        self.address.owned_by.connect(self.pleb)
        self.pleb.address.connect(self.address)
        self.url = "http://testserver"

    def test_unauthorized(self):
        url = reverse('address-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-list')
        data = {'this': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-list')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-list')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-list')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-list')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
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
        url = reverse('address-list')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data['detail'],
                         'Method "DELETE" not allowed.')

    def test_get_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(self.address.object_uuid, response.data['id'])

    def test_get_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual('address', response.data['type'])

    def test_get_street(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual('3295 Rio Vista St', response.data['street'])

    def test_get_street_additional(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        response = self.client.get(url, format='json')
        self.assertIsNone(response.data['street_additional'])

    def test_get_city(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['city'], "Commerce Township")

    def test_get_state(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['state'], 'MI')

    def test_get_postal_code(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['postal_code'], "48382")

    def test_get_congressional_district(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['congressional_district'], 11)

    def test_get_validated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        response = self.client.get(url, format='json')
        self.assertFalse(response.data['validated'])

    def test_address_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-list')
        response = self.client.get(url, format='json')

        self.assertGreater(response.data['count'], 0)

    def test_create_address(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-list')
        data = {
            'city': "Walled Lake",
            'longitude': -83.48016,
            'state': "MI",
            'street': "300 Eagle Pond Dr.",
            'postal_code': "48390-3071",
            'congressional_district': "11",
            'latitude': 42.54083
        }
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['congressional_district'], 11)
        query = 'MATCH (a:Pleb {username: "%s"})-[:LIVES_AT]->' \
                '(b:Address {object_uuid: "%s"}) ' \
                'RETURN b' % (self.user.username, response.data['id'])
        res, col = db.cypher_query(query)
        self.assertEqual(Address.inflate(res[0][0]).object_uuid,
                         response.data['id'])
        query = 'MATCH (a:Pleb)<-[:LIVES_IN]-' \
                '(b:Address {object_uuid: "%s"}) RETURN a' % (
                    response.data['object_uuid'])
        res, col = db.cypher_query(query)
        self.assertEqual(Pleb.inflate(res[0][0]).username, self.user.username)

    def test_update(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        data = {
            'city': "Walled Lake",
            'longitude': -83.48016,
            'state': "MI",
            'street': "300 Eagle Pond Dr.",
            'postal_code': "48390-3071",
            'congressional_district': "11",
            'latitude': 42.54083
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)


class ReputationMethodEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'reputation'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"

    def test_unauthorized(self):
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        data = {'this': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_reputation(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['reputation'], 0)

    def test_get_reputation_increase(self):
        self.client.force_authenticate(user=self.user)
        self.pleb.reputation = 10
        self.pleb.save()
        cache.clear()
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['reputation'], 10)

    def test_get_reputation_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-reputation', kwargs={
            'username': self.user.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BetaUserMethodEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'is_beta_user'
        self.email = "success@simulator.amazonses.com"
        try:
            self.pleb = Pleb.nodes.get(email=self.email)
            self.pleb.delete()
        except:
            pass
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"

    def test_unauthorized(self):
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        data = {'this': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_is_beta_user_default(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        response = self.client.get(url, format='json')
        self.assertFalse(response.data['is_beta_user'])

    def test_get_is_beta_user_true(self):
        self.client.force_authenticate(user=self.user)
        beta_user = BetaUser(email=self.email, invited=True).save()
        self.pleb.beta_user.connect(beta_user)
        self.pleb.save()
        cache.clear()
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        response = self.client.get(url, format='json')
        self.pleb.beta_user.disconnect(beta_user)
        self.pleb.save()
        self.assertTrue(response.data['is_beta_user'])

    def test_get_is_beta_user_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-is-beta-user', kwargs={
            'username': self.user.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class NewsfeedTests(APITestCase):
    def setUp(self):
        query = "match (n)-[r]-() delete n,r"
        db.cypher_query(query)
        cache.clear()
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        while not res['task_id'].ready():
            time.sleep(.1)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.address = Address(street="3295 Rio Vista St",
                               city="Commerce Township", state="MI",
                               postal_code="48382", country="US",
                               congressional_district="11")
        self.address.save()
        self.address.owned_by.connect(self.pleb)
        self.pleb.address.connect(self.address)
        self.url = "http://testserver"

    def test_unauthorized(self):
        url = reverse('me-newsfeed')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        data = {'this': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        data = {}
        response = self.client.post(url, data=data, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['status_code'],
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data['detail'],
                         'Method "DELETE" not allowed.')

    def test_get_count(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'], 0)

    def test_get_success(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_posts(self):
        post = Post(content="Hey I'm a post",
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        post.posted_on_wall.connect(self.pleb.get_wall())
        self.pleb.get_wall().posts.connect(post)
        self.pleb.posts.connect(post)
        post.owned_by.connect(self.pleb)

        post_two = Post(content="Hey I'm a post",
                        owner_username=self.pleb.username,
                        wall_owner_username=self.pleb.username).save()
        post_two.owned_by.connect(self.pleb)
        post_two.posted_on_wall.connect(self.pleb.get_wall())
        self.pleb.get_wall().posts.connect(post_two)
        self.pleb.posts.connect(post_two)
        post_two.owned_by.connect(self.pleb)

        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'], 2)

    def test_get_post_content(self):
        content = "Hey I'm a post"
        post = Post(content=content,
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        post.posted_on_wall.connect(self.pleb.get_wall())
        self.pleb.get_wall().posts.connect(post)
        self.pleb.posts.connect(post)
        post.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['content'], content)

    def test_get_post_content_rendered(self):
        content = "Hey I'm a post"
        post = Post(content=content,
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        post.posted_on_wall.connect(self.pleb.get_wall())
        self.pleb.get_wall().posts.connect(post)
        self.pleb.posts.connect(post)
        post.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertTrue('html' in response.data['results'][0])

    def test_get_post_content_rendered_expedite(self):
        content = "Hey I'm a post"
        post = Post(content=content,
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        post.posted_on_wall.connect(self.pleb.get_wall())
        self.pleb.get_wall().posts.connect(post)
        self.pleb.posts.connect(post)
        post.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true&expedite=true" % reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertTrue('html' in response.data['results'][0])

    def test_get_post_username(self):
        content = "Hey I'm a post"
        post = Post(content=content,
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        post.posted_on_wall.connect(self.pleb.get_wall())
        self.pleb.get_wall().posts.connect(post)
        self.pleb.posts.connect(post)
        post.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['profile'],
                         self.pleb.username)

    def test_get_campaigns(self):
        campaign = PoliticalCampaign(
            active=True, biography="Hey there this is my campaign. "
                                   "Feel free to drop me a line!",
            facebook="dbleibtrey", youtube="devonbleibtrey",
            website="www.sagebrew.com", owner_username=self.pleb.username,
            first_name=self.pleb.first_name, last_name=self.pleb.last_name,
            profile_pic=self.pleb.profile_pic).save()
        campaign.owned_by.connect(self.pleb)
        self.pleb.campaign.connect(campaign)
        usa = Location(name="United States of America").save()
        pres = Position(name="President").save()
        usa.positions.connect(pres)
        pres.location.connect(usa)
        campaign.position.connect(pres)
        pres.campaigns.connect(campaign)
        self.address.encompassed_by.connect(usa)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'], 1)

    def test_get_campaigns_website(self):
        website = "www.sagebrew.com"
        campaign = PoliticalCampaign(
            active=True, biography="Hey there this is my campaign. "
                                   "Feel free to drop me a line!",
            facebook="dbleibtrey", youtube="devonbleibtrey",
            website=website, owner_username=self.pleb.username,
            first_name=self.pleb.first_name, last_name=self.pleb.last_name,
            profile_pic=self.pleb.profile_pic).save()
        campaign.owned_by.connect(self.pleb)
        self.pleb.campaign.connect(campaign)
        usa = Location(name="United States of America").save()
        pres = Position(name="President").save()
        usa.positions.connect(pres)
        pres.location.connect(usa)
        campaign.position.connect(pres)
        pres.campaigns.connect(campaign)
        self.address.encompassed_by.connect(usa)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['website'], website)

    def test_get_campaigns_rendered(self):
        campaign = PoliticalCampaign(
            active=True, biography="Hey there this is my campaign. "
                                   "Feel free to drop me a line!",
            facebook="dbleibtrey", youtube="devonbleibtrey",
            website="www.sagebrew.com", owner_username=self.pleb.username,
            first_name=self.pleb.first_name, last_name=self.pleb.last_name,
            profile_pic=self.pleb.profile_pic).save()
        campaign.owned_by.connect(self.pleb)
        self.pleb.campaign.connect(campaign)
        usa = Location(name="United States of America").save()
        pres = Position(name="President").save()
        usa.positions.connect(pres)
        pres.location.connect(usa)
        campaign.position.connect(pres)
        pres.campaigns.connect(campaign)
        self.address.encompassed_by.connect(usa)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertTrue('html' in response.data['results'][0])

    def test_get_campaigns_rendered_expedite(self):
        campaign = PoliticalCampaign(
            active=True, biography="Hey there this is my campaign. "
                                   "Feel free to drop me a line!",
            facebook="dbleibtrey", youtube="devonbleibtrey",
            website="www.sagebrew.com", owner_username=self.pleb.username,
            first_name=self.pleb.first_name, last_name=self.pleb.last_name,
            profile_pic=self.pleb.profile_pic).save()
        campaign.owned_by.connect(self.pleb)
        self.pleb.campaign.connect(campaign)
        usa = Location(name="United States of America").save()
        pres = Position(name="President").save()
        usa.positions.connect(pres)
        pres.location.connect(usa)
        campaign.position.connect(pres)
        pres.campaigns.connect(campaign)
        self.address.encompassed_by.connect(usa)
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true&expedite=true" % reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertTrue('html' in response.data['results'][0])

    def test_get_campaigns_title(self):
        campaign = PoliticalCampaign(
            active=True, biography="Hey there this is my campaign. "
                                   "Feel free to drop me a line!",
            facebook="dbleibtrey", youtube="devonbleibtrey",
            website="www.sagebrew.com", owner_username=self.pleb.username,
            first_name=self.pleb.first_name, last_name=self.pleb.last_name,
            profile_pic=self.pleb.profile_pic).save()
        campaign.owned_by.connect(self.pleb)
        self.pleb.campaign.connect(campaign)
        usa = Location(name="United States of America").save()
        pres = Position(name="President").save()
        usa.positions.connect(pres)
        pres.location.connect(usa)
        campaign.position.connect(pres)
        pres.campaigns.connect(campaign)
        self.address.encompassed_by.connect(usa)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['owner_username'],
                         self.pleb.username)

    def test_get_question_content(self):
        content = "This is the content for my question."
        question = Question(
            title="Hello there world",
            content=content,
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['content'], content)

    def test_get_question_title(self):
        content = "This is the content for my question."
        title = "Hello there world"
        question = Question(
            title=title,
            content=content,
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['title'], title)

    def test_get_question_profile(self):
        content = "This is the content for my question."
        title = "Hello there world"
        question = Question(
            title=title,
            content=content,
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['profile'],
                         self.pleb.username)

    def test_get_question_multiple(self):
        content = "This is the content for my question."
        title = "Hello there world"
        question = Question(
            title=title,
            content=content,
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        question_two = Question(
            title=title,
            content=content,
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question_two)
        question_two.owned_by.connect(self.pleb)

        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'], 2)

    def test_get_question_rendered(self):
        content = "This is the content for my question."
        title = "Hello there world"
        question = Question(
            title=title,
            content=content,
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertTrue('html' in response.data['results'][0])

    def test_get_question_rendered_expedite(self):
        content = "This is the content for my question."
        title = "Hello there world"
        question = Question(
            title=title,
            content=content,
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        self.client.force_authenticate(user=self.user)
        url = "%s?html=true&expedite=true" % reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertTrue('html' in response.data['results'][0])

    def test_get_solution_content(self):
        content = 'this is fake content'
        question = Question(
            title="Hello there world",
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        solution = Solution(content=content,
                            owner_username=self.pleb.username).save()
        solution.owned_by.connect(self.pleb)
        self.pleb.solutions.connect(solution)
        question.solutions.connect(solution)
        solution.solution_to.connect(question)

        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['content'], content)

    def test_get_solution_profile(self):
        content = 'this is fake content'
        question = Question(
            title="Hello there world",
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        solution = Solution(content=content,
                            owner_username=self.pleb.username).save()
        solution.owned_by.connect(self.pleb)
        self.pleb.solutions.connect(solution)
        question.solutions.connect(solution)
        solution.solution_to.connect(question)

        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['profile'],
                         self.pleb.username)

    def test_get_solution_multiple(self):
        content = 'this is fake content'
        question = Question(
            title="Hello there world",
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        solution = Solution(content=content,
                            owner_username=self.pleb.username).save()
        solution.owned_by.connect(self.pleb)
        self.pleb.solutions.connect(solution)

        solution_two = Solution(content=content,
                                owner_username=self.pleb.username).save()
        solution_two.owned_by.connect(self.pleb)
        self.pleb.solutions.connect(solution_two)
        question.solutions.connect(solution)
        solution.solution_to.connect(question)

        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'], 2)

    def test_get_solution_rendered(self):
        content = 'this is fake content'
        question = Question(
            title="Hello there world",
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        solution = Solution(content=content,
                            owner_username=self.pleb.username).save()
        solution.owned_by.connect(self.pleb)
        self.pleb.solutions.connect(solution)
        question.solutions.connect(solution)
        solution.solution_to.connect(question)

        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertTrue('html' in response.data['results'][0])

    def test_get_solution_rendered_expedite(self):
        content = 'this is fake content'
        question = Question(
            title="Hello there world",
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        solution = Solution(content=content,
                            owner_username=self.pleb.username).save()
        solution.owned_by.connect(self.pleb)
        self.pleb.solutions.connect(solution)
        question.solutions.connect(solution)
        solution.solution_to.connect(question)

        self.client.force_authenticate(user=self.user)
        url = "%s?html=true&expedite=true" % reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertTrue('html' in response.data['results'][0])

    def test_get_multiple_objects(self):
        post = Post(content="Hey I'm a post",
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        post.posted_on_wall.connect(self.pleb.get_wall())
        self.pleb.get_wall().posts.connect(post)
        self.pleb.posts.connect(post)
        post.owned_by.connect(self.pleb)

        question = Question(
            title="Hello there world",
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        solution = Solution(content='this is fake content',
                            owner_username=self.pleb.username).save()
        solution.owned_by.connect(self.pleb)
        question.solutions.connect(solution)
        solution.solution_to.connect(question)
        self.pleb.solutions.connect(solution)
        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['count'], 3)

    def test_get_multiple_objects_ordering(self):
        post = Post(content="Hey I'm a post",
                    owner_username=self.pleb.username,
                    wall_owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        post.posted_on_wall.connect(self.pleb.get_wall())
        self.pleb.get_wall().posts.connect(post)
        self.pleb.posts.connect(post)
        post.owned_by.connect(self.pleb)

        question = Question(
            title="Hello there world",
            content="This is the content for my question.",
            owner_username=self.pleb.username).save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)

        solution = Solution(content='this is fake content',
                            owner_username=self.pleb.username).save()
        solution.owned_by.connect(self.pleb)
        question.solutions.connect(solution)
        solution.solution_to.connect(question)
        self.pleb.solutions.connect(solution)

        self.client.force_authenticate(user=self.user)
        url = reverse('me-newsfeed')
        response = self.client.get(url, format='json')
        # This assumes that the above ordering creates the post first,
        # then the question, then the solution. The newsfeed should order
        # these in reverse based on their date created.
        self.assertEqual(response.data['results'][0]['type'], 'solution')
        self.assertEqual(response.data['results'][1]['type'], 'question')
        self.assertEqual(response.data['results'][2]['type'], 'post')


class TestAcceptFriendRequest(APITestCase):
    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.email2 = "bounce@simulator.amazonses.com"
        res = create_user_util_test(self.email2)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb2 = Pleb.nodes.get(email=self.email2)
        self.user2 = User.objects.get(email=self.email2)

    def test_unauthorized(self):
        data = {}
        url = reverse('friend_request-accept',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        data = {'this': ['This field is required.']}
        url = reverse('friend_request-accept',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-accept',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-accept',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-accept',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-accept',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_accept_success(self):
        self.client.force_authenticate(user=self.user)
        friend_request = FriendRequest().save()
        url = reverse('friend_request-accept',
                      kwargs={'object_uuid': friend_request.object_uuid})
        pleb = Pleb.nodes.get(email=self.user.email)
        pleb2 = Pleb.nodes.get(email=self.user2.email)
        data = {
            'request_id': friend_request.object_uuid,
        }
        friend_request.request_to.connect(pleb2)
        friend_request.request_from.connect(pleb)
        pleb.friend_requests_sent.connect(friend_request)
        pleb2.friend_requests_received.connect(friend_request)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'],
                         "Successfully accepted friend request.")

    def test_accept_non_existent_request(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'request_id': str(uuid1()),
        }
        url = reverse('friend_request-accept',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'],
                         'Sorry this object does not exist.')


class TestDeclineFriendRequest(APITestCase):
    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.email2 = "bounce@simulator.amazonses.com"
        res = create_user_util_test(self.email2)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb2 = Pleb.nodes.get(email=self.email2)
        self.user2 = User.objects.get(email=self.email2)

    def test_unauthorized(self):
        data = {}
        url = reverse('friend_request-decline',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        data = {'this': ['This field is required.']}
        url = reverse('friend_request-decline',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-decline',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-decline',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-decline',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-decline',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_decline_success(self):
        self.client.force_authenticate(user=self.user)
        friend_request = FriendRequest().save()
        url = reverse('friend_request-decline',
                      kwargs={'object_uuid': friend_request.object_uuid})
        pleb = Pleb.nodes.get(email=self.user.email)
        pleb2 = Pleb.nodes.get(email=self.user2.email)
        data = {
            'request_id': friend_request.object_uuid,
        }
        friend_request.request_to.connect(pleb2)
        friend_request.request_from.connect(pleb)
        pleb.friend_requests_sent.connect(friend_request)
        pleb2.friend_requests_received.connect(friend_request)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'],
                         "Successfully declined friend request.")

    def test_decline_non_existent_request(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'request_id': str(uuid1()),
        }
        url = reverse('friend_request-decline',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'],
                         'Sorry this object does not exist.')


class TestBlockFriendRequest(APITestCase):
    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.email2 = "bounce@simulator.amazonses.com"
        res = create_user_util_test(self.email2)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb2 = Pleb.nodes.get(email=self.email2)
        self.user2 = User.objects.get(email=self.email2)

    def test_unauthorized(self):
        data = {}
        url = reverse('friend_request-block',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        data = {'this': ['This field is required.']}
        url = reverse('friend_request-block',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-block',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-block',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-block',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-block',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_block_success(self):
        self.client.force_authenticate(user=self.user)
        friend_request = FriendRequest().save()
        url = reverse('friend_request-block',
                      kwargs={'object_uuid': friend_request.object_uuid})
        pleb = Pleb.nodes.get(email=self.user.email)
        pleb2 = Pleb.nodes.get(email=self.user2.email)
        data = {
            'request_id': friend_request.object_uuid,
        }
        friend_request.request_to.connect(pleb2)
        friend_request.request_from.connect(pleb)
        pleb.friend_requests_sent.connect(friend_request)
        pleb2.friend_requests_received.connect(friend_request)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'],
                         "Successfully blocked further friend requests.")

    def test_block_non_existent_request(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'request_id': str(uuid1()),
        }
        url = reverse('friend_request-block',
                      kwargs={'object_uuid': str(uuid1())})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'],
                         'Sorry this object does not exist.')
