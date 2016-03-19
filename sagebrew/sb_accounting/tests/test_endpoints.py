import pytz
import stripe
import calendar
import requests_mock
from datetime import datetime

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

    @requests_mock.mock()
    def test_valid_event_request_account_updated(self, m):
        self.quest.account_verified = "unverified"
        self.quest.save()
        cache.clear()
        event_mock_data = {
            "id": "evt_00000000000000",
            "type": "account.updated",
            "data": {
                "object": {
                    "id": "acct_00000000000000"
                }
            }
        }
        m.get("https://api.stripe.com/v1/events/evt_00000000000000",
              json=event_mock_data, status_code=status.HTTP_200_OK)
        account_mock_data = {
            "email": "success@simulator.amazonses.com",
            "verification": {
                "fields_needed": []
            },
            "legal_entity": {
                "verification": {
                    "status": "verified",
                    "details": ["some", "reasons", "this", "failed"]
                }
            }
        }
        m.get("https://api.stripe.com/v1/accounts/acct_00000000000000",
              json=account_mock_data, status_code=status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000"
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Account Updated")

    @requests_mock.mock()
    def test_valid_event_request_transfer_failed_stripe_account(self, m):
        self.quest.account_verified = "unverified"
        self.quest.save()
        cache.clear()
        event_mock_data = {
            "id": "evt_00000000000000",
            "type": "transfer.failed",
            "data": {
                "object": {
                    "id": "tr_00000000000000"
                }
            }
        }
        m.get("https://api.stripe.com/v1/events/evt_00000000000000",
              json=event_mock_data, status_code=status.HTTP_200_OK)
        transfer_mock_data = {
            "type": "stripe_account",
            "destination": "acct_00000000000000"
        }
        m.get("https://api.stripe.com/v1/transfers/tr_00000000000000",
              json=transfer_mock_data, status_code=status.HTTP_200_OK)
        account_mock_data = {
            "email": "success@simulator.amazonses.com"
        }
        m.get("https://api.stripe.com/v1/accounts/acct_00000000000000",
              json=account_mock_data, status_code=status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000"
        }
        intercom_mock_data = {
            "event_name": "stripe-transfer-failed",
            "user_id": self.pleb.username,
            "created": calendar.timegm(datetime.now(pytz.utc).utctimetuple())
        }
        m.post("https://api.intercom.io/events/", json=intercom_mock_data,
               status_code=status.HTTP_202_ACCEPTED)
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Transfer Failed")

    @requests_mock.mock()
    def test_valid_event_request_trial_will_end(self, m):
        self.quest.account_verified = "unverified"
        self.quest.save()
        cache.clear()
        event_mock_data = {
            "id": "evt_00000000000000",
            "type": "customer.subscription.trial_will_end",
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
        self.assertEqual(response.data['detail'], "Trail Will End")
