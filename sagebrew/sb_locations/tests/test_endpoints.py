from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.cache import cache

from neomodel import db

from rest_framework import status
from rest_framework.test import APITestCase

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_locations.neo_models import Location


class LocationEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'location'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.location = Location(name="Michigan").save()
        cache.clear()

    def test_unauthorized(self):
        url = reverse('location-list')
        response = self.client.post(url, {}, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-list')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-list')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-list')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-list')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-detail',
                      kwargs={'object_uuid': self.location.object_uuid})
        response = self.client.post(url, data={}, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-detail',
                      kwargs={'object_uuid': self.location.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_name(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-detail',
                      kwargs={'object_uuid': self.location.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['name'], self.location.name)

    def test_detail_encompasses(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-detail',
                      kwargs={'object_uuid': self.location.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['encompasses'], [])

    def test_detail_encompassed_by(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-detail',
                      kwargs={'object_uuid': self.location.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['encompassed_by'], [])

    def test_detail_geo_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-detail',
                      kwargs={'object_uuid': self.location.object_uuid})
        response = self.client.get(url)

        self.assertFalse(response.data['geo_data'])

    def test_detail_positions(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-detail',
                      kwargs={'object_uuid': self.location.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['positions'], [])

    def test_detail_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-detail',
                      kwargs={'object_uuid': self.location.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['id'], self.location.object_uuid)

    def test_detail_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-detail',
                      kwargs={'object_uuid': self.location.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['type'], self.unit_under_test_name)

    def test_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_non_admin(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-add')
        response = self.client.post(url, {
            "name": "Wixom",
            "geo_data": None,
            "encompassed_by_name": "Michigan",
            "encompassed_by_uuid": ""
        }, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_add_anon(self):
        url = reverse('location-add')
        response = self.client.post(url, {
            "name": "Wixom",
            "geo_data": None,
            "encompassed_by_name": "Michigan",
            "encompassed_by_uuid": ""
        }, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_add_admin(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('location-add')
        response = self.client.post(url, {
            "name": "Wixom",
            "geo_data": None,
            "encompassed_by_name": self.location.name,
            "encompassed_by_uuid": ""
        }, format='json')
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Wixom')
        self.assertEqual(response.data['geo_data'], False)
        self.assertIn(self.location.object_uuid,
                      response.data['encompassed_by'])

    def test_add_get(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('location-add')
        response = self.client.get(url)
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_add_uuid(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('location-add')
        response = self.client.post(url, {
            "name": "City of Wixom",
            "geo_data": None,
            "encompassed_by_name": "",
            "encompassed_by_uuid": self.location.object_uuid
        }, format='json')
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'City of Wixom')
        self.assertEqual(response.data['geo_data'], False)
        self.assertIn(self.location.object_uuid,
                      response.data['encompassed_by'])

    def test_add_invalid_serializer(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('location-add')
        response = self.client.post(url, {
            "name": "Wixom City",
            "encompassed_by_uuid": self.location.object_uuid
        }, format='json')
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
