from base64 import b64encode
from django.conf import settings
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from sb_registration.utils import create_user_util_test


class MeEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.unit_under_test = create_user_util_test("test@sagebrew.com")
        self.url = "http://testserver"

    def test_unauthorized(self):
        url = reverse('me-detail')
        data = {}
        response = self.client.post(url, data, format='json')
        unauthorized = {
            'detail': 'Authentication credentials were not provided.'
        }
        self.assertEqual(response.data, unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        data = {'projects': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code, 400)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code, 400)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code, 400)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code, 400)

    def test_save_image_data(self):
        with open(settings.PROJECT_DIR + "/images/test_image.jpg",
                  "rb") as image_file:
            image = b64encode(image_file.read())
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        response = self.client.post(url, image, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me-detail')
        data = {}
        response = self.client.post(url, data=data, format='json')
        response_data = {'detail': 'Method "POST" not allowed.'}
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

    def test_read(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'uuid': self.unit_under_test.uuid})

        response = self.client.get(url, format='json')
        data = {
            'uuid': self.unit_under_test.uuid,
            'url': "%s/v1/addresses/%s/" % (self.url, response.data["uuid"]),
            'first_name': 'Receiver',
            'last_name': 'Test',
            'address_additional': 'Apt 138',
            'address': '300 Eagle Pond Dr.',
            'city': 'Walled Lake',
            'country': 'US',
            'zipcode': '48390',
            'state': 'MI',
            'company': 'Test Company'
        }
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_expanded(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'uuid': self.unit_under_test.uuid})

        response = self.client.get(url, format='json')
        data = {
            'uuid': self.unit_under_test.uuid,
            'url': "%s/v1/addresses/%s/" % (self.url, response.data["uuid"]),
            'first_name': 'Receiver',
            'last_name': 'Test',
            'address_additional': 'Apt 138',
            'address': '300 Eagle Pond Dr.',
            'city': 'Walled Lake',
            'country': 'US',
            'zipcode': '48390',
            'state': 'MI',
            'company': 'Test Company'
        }
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
