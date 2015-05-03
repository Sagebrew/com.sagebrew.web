import shortuuid

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework import status
from rest_framework.test import APITestCase

from sagebrew import errors
from plebs.neo_models import Pleb, FriendRequest
from sb_questions.neo_models import Question
from sb_registration.utils import create_user_util_test


class MeEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
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

    def test_get_friend_request_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.friend_request.object_uuid)

    def test_get_friend_request_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], "friend_request")

    def test_get_friend_request_seen(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['seen'])

    def test_get_friend_request_time_sent(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['time_sent'],
                         self.friend_request.time_sent.isoformat()[:-6] + 'Z')

    def test_get_friend_request_time_seen(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['time_seen'],
                         self.friend_request.time_seen)

    def test_get_friend_request_response(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['response'])

    def test_get_friend_request_from_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['from_user'],
                         "http://testserver/v1/profiles/test_test1/")

    def test_get_friend_request_to_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('friend_request-detail',
                      kwargs={"object_uuid": self.friend_request.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['to_user'],
                         "http://testserver/v1/profiles/test_test/")

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
            content="This is the content for my question.").save()
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
            content="This is the content for my question.").save()
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
            content="This is the content for my question.").save()
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
            content="This is the content for my question.").save()
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
            content="This is the content for my question.").save()
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
            content="This is the content for my question.").save()
        self.pleb.questions.connect(question)
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-questions', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['profile'],
                         "http://testserver/v1/profiles/test_test/")

    def test_get_pleb_question_url(self):
        for item in Question.nodes.all():
            item.delete()
        question = Question(
            title="Hello there world",
            content="This is the content for my question.").save()
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
            content="This is the content for my question.").save()
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
        question = Question(
            title="Hello there world",
            content="This is the content for my question.").save()
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

    def test_get_pleb_friends_id(self):
        friend = Pleb(username=shortuuid.uuid()).save()
        self.pleb.friends.connect(friend)

        friend.friends.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-friends', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'][0]['id'], friend.username)

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

    def test_get_pleb_friend_requests(self):
        friend = Pleb(username=shortuuid.uuid()).save()
        friend_request = FriendRequest().save()
        friend_request.request_from.connect(friend)
        friend_request.request_to.connect(self.pleb)
        self.client.force_authenticate(user=self.user)

        url = "%s" % reverse('profile-friend-requests', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_other_users_friend_requests(self):
        email = "bounce@simulator.amazonses.com"
        create_user_util_test(email)
        friend = Pleb(username=shortuuid.uuid()).save()
        friend_request = FriendRequest().save()
        self.pleb.friend_requests_sent.connect(friend_request)
        friend.friend_requests_received.connect(friend_request)
        friend_request.request_from.connect(self.pleb)
        friend_request.request_to.connect(friend)
        self.client.force_authenticate(user=User.objects.get(email=email))

        url = "%s" % reverse('profile-friend-requests', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data,
                         {"detail": "You can only get"
                                    " your own friend requests"})

    def test_get_no_friend_requests(self):
        self.client.force_authenticate(user=self.user)

        url = "%s" % reverse('profile-friend-requests', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_no_friend_requests_html(self):
        self.client.force_authenticate(user=self.user)

        url = "%s?html=true" % reverse('profile-friend-requests', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, '<div id="friend_request_wrapper">\n'
                                        '    \n</div>')

    def test_get_friend_requests_html(self):
        email = "bounce@simulator.amazonses.com"
        create_user_util_test(email)
        friend = Pleb(username=shortuuid.uuid()).save()
        friend_request = FriendRequest().save()
        self.pleb.friend_requests_sent.connect(friend_request)
        friend.friend_requests_received.connect(friend_request)
        friend_request.request_from.connect(self.pleb)
        friend_request.request_to.connect(friend)
        self.client.force_authenticate(user=self.user)

        url = "%s?html=true" % reverse('profile-friend-requests', kwargs={
            'username': self.pleb.username})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
