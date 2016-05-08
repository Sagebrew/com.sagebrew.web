from uuid import uuid1
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings

from neomodel import db

from rest_framework import status
from rest_framework.test import APITestCase

from sb_public_official.neo_models import PublicOfficial
from sb_locations.neo_models import Location
from sb_registration.utils import create_user_util_test

from sb_address.neo_models import Address


class AddressEndpointTests(APITestCase):

    def setUp(self):
        query = 'MATCH (a) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        self.unit_under_test_name = 'address'
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        PublicOfficial(bioguideid=str(uuid1()), title="President",
                       gt_id=str(uuid1())).save()
        self.address = Address(street="3295 Rio Vista St",
                               city="Commerce Township", state="MI",
                               postal_code="48382", country="US",
                               congressional_district="11")
        self.address.save()
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
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

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

    def test_update_no_matching_location(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        data = {
            'city': "Walled Lake",
            'longitude': -83.48016,
            'state': "MI",
            'street': "300 Eagle Pond Dr.",
            'postal_code': "48390-3071",
            'congressional_district': "100",
            'latitude': 42.54083
        }
        response = self.client.put(url, data=data, format='json')
        settings.CELERY_ALWAYS_EAGER = False
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_with_matching_location(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.client.force_authenticate(user=self.user)
        url = reverse('address-detail', kwargs={
            'object_uuid': self.address.object_uuid})
        state = Location(name="Michigan").save()
        district = Location(name="10", sector="federal").save()
        state.encompasses.connect(district)
        district.encompassed_by.connect(state)
        data = {
            'city': "Walled Lake",
            'longitude': -83.48016,
            'state': "MI",
            'street': "300 Eagle Pond Dr.",
            'postal_code': "48390-3071",
            'congressional_district': "10",
            'latitude': 42.54083
        }
        response = self.client.put(url, data=data, format='json')
        settings.CELERY_ALWAYS_EAGER = False
        address = Address.nodes.get(object_uuid=response.data['id'])
        self.assertIn(district, address.encompassed_by)
