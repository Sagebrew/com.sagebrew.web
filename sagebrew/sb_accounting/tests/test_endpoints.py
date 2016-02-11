import stripe
import requests_mock

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from neomodel import db

from sb_registration.utils import create_user_util_test

from sb_quests.neo_models import Quest


class AccountingHooksTests(APITestCase):

    def setUp(self):
        query = "match (n)-[r]-() delete n,r"
        db.cypher_query(query)
        self.unit_under_test_name = 'accounting'
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        self.quest.editors.connect(self.pleb)
        self.quest.moderators.connect(self.pleb)
        cache.clear()
        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_SECRET_KEY

    def test_invalid_event_request(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000"
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @requests_mock.mock()
    def test_valid_event_request(self, m):
        event_mock_data = {
            "id": "evt_00000000000000",
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "customer": "cus_00000000000000"
                }
            }
        }
        m.get("https://api.stripe.com/v1/events/evt_00000000000000",
              json=event_mock_data, status_code=status.HTTP_200_OK)
        customer_mock_data = {
            "email": "success@simulator.amazonses.com"
        }
        m.get("https://api.stripe.com/v1/customers/cus_00000000000000",
              json=customer_mock_data, status_code=status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000"
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Invoice Payment Failed")

    @requests_mock.mock()
    def test_valid_event_invalid_customer_request(self, m):
        event_mock_data = {
            "id": "evt_00000000000000",
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "customer": "cus_00000000000000"
                }
            }
        }
        m.get("https://api.stripe.com/v1/events/evt_00000000000000",
              json=event_mock_data, status_code=status.HTTP_200_OK)
        customer_mock_data = {
            "error": {
                "type": "invalid_request_error"
            }
        }
        m.get("https://api.stripe.com/v1/customers/cus_00000000000000",
              json=customer_mock_data, status_code=status.HTTP_400_BAD_REQUEST)
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000"
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)