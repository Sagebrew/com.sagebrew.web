import stripe
import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework import status
from rest_framework.test import APITestCase

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

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
        response = self.client.post(url, {}, format='json')
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
        response = self.client.post(url, {}, format='json')
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
                         "query all donations for every quest.")
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

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

    def test_get_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['type'], 'donation')

    def test_get_completed(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['completed'], self.donation.completed)

    def test_get_amount(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['amount'], self.donation.amount)

    def test_get_owner_username(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['owner_username'],
                         self.donation.owner_username)

    def test_get_quest(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.get(url)

        self.assertIsNone(response.data['quest'])

    def test_get_mission(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.get(url)
        self.assertIsNone(response.data['mission'])

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
                         status.HTTP_204_NO_CONTENT)

    def test_delete_not_owner(self):
        self.email2 = "bounce@simulator.amazonses.com"
        res = create_user_util_test(self.email2, task=True)
        self.assertNotEqual(res, False)
        self.user2 = User.objects.get(email=self.email2)
        self.client.force_authenticate(user=self.user2)
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.delete(url, data={}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_completed(self):
        self.client.force_authenticate(user=self.user)
        self.donation.completed = True
        self.donation.save()
        url = reverse('donation-detail',
                      kwargs={'object_uuid': self.donation.object_uuid})
        response = self.client.delete(url, data={}, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_403_FORBIDDEN)


class TestSagebrewDonation(APITestCase):
    def setUp(self):
        cache.clear()
        self.unit_under_test_name = 'donations'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.donation = Donation(completed=False, amount=1000,
                                 owner_username=self.user.username).save()
        self.pleb.is_verified = True
        self.pleb.save()
        cache.set(self.pleb.username, self.pleb)

    def test_unauthorized(self):
        url = reverse('direct_donation')
        response = self.client.post(url, {}, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('direct_donation')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('direct_donation')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('direct_donation')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('direct_donation')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('direct_donation')
        response = self.client.get(url)

        self.assertEqual(response.data['detail'], 'Method "GET" not allowed.')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('direct_donation')
        response = self.client.get(url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_donation_create_invalid_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('direct_donation')
        stripe.api_key = settings.STRIPE_SECRET_KEY
        token = stripe.Token.create(
            card={
                "number": "4242424242424242",
                "exp_month": 12,
                "exp_year": (datetime.datetime.now() + datetime.timedelta(
                    days=3 * 365)).year,
                "cvc": '123'
            }
        )
        data = {
            'token': token['id']
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_donation_create_user_is_not_verified(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('direct_donation')
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.pleb.stripe_customer_id = None
        self.pleb.is_verified = False
        self.pleb.save()
        cache.clear()
        token = stripe.Token.create(
            card={
                "number": "4242424242424242",
                "exp_month": 12,
                "exp_year": (datetime.datetime.now() + datetime.timedelta(
                    days=3 * 365)).year,
                "cvc": '123'
            }
        )
        data = {
            'amount': 1000,
            'token': token['id']
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.pleb.is_verified = True
        self.pleb.save()
