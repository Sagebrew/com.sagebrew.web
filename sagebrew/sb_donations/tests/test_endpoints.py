import pytz
from datetime import datetime

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework import status
from rest_framework.test import APITestCase

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_campaigns.neo_models import PoliticalCampaign, Position
from sb_goals.neo_models import Goal, Round

from sb_donations.neo_models import Donation


class DonationEndpointTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.unit_under_test_name = 'goal'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.donation = Donation(completed=False, amount=1000,
                             owner_username=self.user.username).save()

    def test_unauthorized(self):
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        data = {}
        response = self.client.post(url, data=data, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-list')
        response = self.client.get(url)

        self.assertEqual(response.data['detail'],
                         "Sorry, we currently do not allow for users to "
                         "query all donations for every campaign.")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['id'], self.donation.object_uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['type'], 'donation')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_completed(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['completed'], self.donation.completed)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_amount(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['amount'], self.donation.amount)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_owner_username(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['owner_username'],
                         self.donation.owner_username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_donated_for(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.get(url)

        self.assertIsNone(response.data['donated_for'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_applied_to(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['applied_to'], [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_owned_by(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['owned_by'],
                         self.donation.owner_username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_campaign(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.get(url)

        self.assertIsNone(response.data['campaign'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.put(url, data={}, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.patch(url, data={}, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.post(url, data={}, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.delete(url, data={}, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
