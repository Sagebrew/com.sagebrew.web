from base64 import b64encode
from uuid import uuid1

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from sb_oauth.models import SBApplication


class ApplicationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='lauren', password='secret')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.unit_under_test = SBApplication.objects.create(
            user=self.user, web_hook="http://www.google.com")
        self.unit_under_test_name = "application"
        self.user_url_end = reverse("user-detail", kwargs={
            "username": self.user.username})
        self.user_url = "%s%s" % ("http://testserver", self.user_url_end)

    def test_unauthorized(self):
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {}
        response = self.client.post(url, data, format='json')
        unauthorized = 'Authentication credentials were not provided.'
        self.assertEqual(response.data['detail'], unauthorized)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {'asset_uri': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code, 400)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code, 400)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code, 400)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code, 400)

    def test_save_image_data(self):
        with open(settings.PROJECT_DIR + "/sagebrew/static/favicon.ico",
                  "rb") as image_file:
            image = b64encode(image_file.read())
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, image, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)

        data = {
            "user": self.user_url,
            "redirect_uris": "http://google.com",
            "client_type": "confidential",
            "authorization_grant_type": "password",
            "name": "the_test",
            "web_hook": "http://google.com"
        }
        response = self.client.post(url, data=data, format='json')
        response_data = {
            "user": self.user_url,
            "client_id": response.data["client_id"],
            "client_secret": response.data["client_secret"],
            "redirect_uris": "http://google.com",
            "client_type": "confidential",
            "authorization_grant_type": "password",
            "name": "the_test",
            "web_hook": "http://google.com"
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'client_id': self.unit_under_test.client_id})
        data = {
            "user": self.user_url,
            "redirect_uris": "http://google.com",
            "client_type": "confidential",
            "authorization_grant_type": "password",
            "name": "the_test",
            "web_hook": "http://google.com"
        }
        response = self.client.post(url, data, format='json')
        response_data = {'detail': 'Method "POST" not allowed.',
                         'status_code': status.HTTP_405_METHOD_NOT_ALLOWED}
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_reset_credentials(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'client_id': self.unit_under_test.client_id})

        data = {
            "user": self.user_url,
            "redirect_uris": "http://google.com",
            "client_type": "public",
            "authorization_grant_type": "password",
            "name": "the_test",
            "web_hook": "http://google.com",
            "reset_credentials": True,
        }
        response = self.client.put(url, data, format='json')
        response_data = {
            'redirect_uris': u'http://google.com',
            'name': u'the_test',
            'client_type': '',
            'web_hook': u'http://google.com',
            'user': self.user_url,
            'client_id': response.data["client_id"],
            'client_secret': response.data["client_secret"],
            'authorization_grant_type': ''
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'client_id': self.unit_under_test.client_id})

        data = {
            "user": self.user_url,
            "redirect_uris": "http://google.com",
            "client_type": "public",
            "authorization_grant_type": "password",
            "name": "the_test",
            "web_hook": "http://google.com"
        }
        response = self.client.put(url, data, format='json')
        response_data = {
            'redirect_uris': u'http://google.com',
            'name': u'the_test',
            'client_type': '',
            'web_hook': u'http://google.com',
            "user": self.user_url,
            'client_id': self.unit_under_test.client_id,
            'client_secret': self.unit_under_test.client_secret,
            'authorization_grant_type': ''
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_does_not_exist(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={"client_id": str(uuid1())})
        data = {'detail': 'Not found.',
                'status_code': status.HTTP_404_NOT_FOUND}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {'detail': 'Method "PUT" not allowed.',
                'status_code': status.HTTP_405_METHOD_NOT_ALLOWED}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'client_id': self.unit_under_test.client_id})
        data = None
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {'detail': 'Method "DELETE" not allowed.',
                'status_code': status.HTTP_405_METHOD_NOT_ALLOWED}
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_read(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'client_id': self.unit_under_test.client_id})
        response = self.client.get(url, format='json')
        data = {
            'redirect_uris': u'',
            'name': u'',
            'client_type': u'',
            'web_hook': u'http://www.google.com',
            'user': self.user_url,
            'client_id': response.data['client_id'],
            'client_secret': response.data["client_secret"],
            'authorization_grant_type': u''}
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.get(url, format='json')
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
