from dateutil.parser import parse

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework import status
from rest_framework.test import APITestCase

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_updates.neo_models import Update


class UpdateEndpointsTest(APITestCase):
    def setUp(self):
        cache.clear()
        self.unit_under_test_name = 'goal'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.update = Update(title="Test Title", content="Test Content",
                             html_content="HTML Content",
                             owner_username=self.pleb.username).save()
        self.update.owned_by.connect(self.pleb)

    def test_unauthorized(self):
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.post(url, {}, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.post(url, {}, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['id'], self.update.object_uuid)

    def test_get_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['type'], 'update')

    def test_get_content(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['content'], self.update.content)

    def test_get_created(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.get(url)

        self.assertEqual(parse(response.data['created']), self.update.created)

    def test_get_upvotes(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['upvotes'], 0)

    def test_get_downvotes(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['downvotes'], 0)

    def test_get_vote_count(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['vote_count'], 0)

    def test_get_vote_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.get(url)

        self.assertIsNone(response.data['vote_type'])

    def test_get_view_count(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['view_count'], 0)

    def test_get_profile(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['profile'], "test_test")

    def test_get_url(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['url'], self.url + url)

    def test_get_last_edited_on(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.get(url)

        self.assertEqual(parse(response.data['last_edited_on']),
                         self.update.last_edited_on)

    def test_get_flagged_by(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['flagged_by'], [])

    def test_get_html_content(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['html_content'], "<p>Test Content</p>")

    def test_get_title(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['title'], self.update.title)

    def test_get_goals(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['goals'], [])

    def test_get_campaign(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.get(url)

        self.assertIsNone(response.data['campaign'])

    def test_put(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        data = {
            'title': 'testing update title',
            'content': 'testing update content'
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['title'], data['title'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_content(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        data = {
            'content': 'testing update'
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['content'], data['content'])

    def test_put_no_content(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        data = {
            'title': 'testing update title'
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['content'], ['This field is required.'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        data = {
            'title': 'testing update title',
        }
        response = self.client.patch(url, data=data, format='json')

        self.assertEqual(response.data['title'], data['title'])
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

    def test_patch_content(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        data = {
            'content': 'testing update'
        }
        response = self.client.patch(url, data=data, format='json')

        self.assertEqual(response.data['content'], data['content'])

    def test_post(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.post(url, data={}, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-detail',
                      kwargs={'object_uuid': self.update.object_uuid})
        response = self.client.delete(url)

        self.assertEqual(response.data['detail'], "Sorry we do not allow "
                                                  "deletion of updates.")
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
