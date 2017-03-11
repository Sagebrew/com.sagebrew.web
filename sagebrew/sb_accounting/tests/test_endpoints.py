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

from neomodel import db, DoesNotExist

from sagebrew.plebs.neo_models import Pleb
from sagebrew.sb_registration.utils import create_user_util_test
from sagebrew.sb_quests.neo_models import Quest


class AccountingHooksTests(APITestCase):

    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        db.cypher_query(query)
        try:
            self.pleb2 = Pleb.nodes.get(
                username=settings.INTERCOM_USER_ID_DEVON)
        except (Pleb.DoesNotExist, DoesNotExist):
            self.pleb2 = Pleb(username=settings.INTERCOM_USER_ID_DEVON).save()
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
        stripe.api_version = settings.STRIPE_API_VERSION
        self.intercom_url = "https://api.intercom.io/admins"

    def tearDown(self):
        self.pleb2.delete()
        cache.clear()

    def test_invalid_event_request(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000"
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @requests_mock.mock()
    def test_valid_event_request(self, m):
        intercom_mock_data = {
            "type": "admin.list",
            "admins": [
                {
                    "type": "admin",
                    "id": "69989",
                    "name": "Devon Bleibtrey",
                    "email": "devon@sagebrew.com"
                }
            ]
        }
        m.get(self.intercom_url, json=intercom_mock_data,
              status_code=status.HTTP_200_OK)
        customer_mock_data = {
            "email": "success@simulator.amazonses.com"
        }
        m.get("https://api.stripe.com/v1/customers/cus_00000000000000",
              json=customer_mock_data, status_code=status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000",
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "customer": "cus_00000000000000"
                }
            }
        }
        m.post("https://api.intercom.io/messages/",
               status_code=status.HTTP_202_ACCEPTED)
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], "Invoice Payment Failed")

    @requests_mock.mock()
    def test_invoice_payment_failed_request_no_user(self, m):
        customer_mock_data = {
            "email": "success@simulator.amazonses.com"
        }
        m.get("https://api.stripe.com/v1/customers/cus_00000000000000",
              json=customer_mock_data, status_code=status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000",
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "customer": "cus_00000000000000"
                }
            }
        }
        query = 'MATCH (pleb:Pleb {email: "%s"})-[r]-() ' \
                'DELETE pleb, r' % "success@simulator.amazonses.com"
        db.cypher_query(query)
        m.post("https://api.intercom.io/messages/",
               status_code=status.HTTP_202_ACCEPTED)
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['id'], "evt_00000000000000")

    @requests_mock.mock()
    def test_valid_event_request_invalid_serializer(self, m):
        intercom_mock_data = {
            "type": "admin.list",
            "admins": [
                {
                    "type": "admin",
                    "id": "123456",
                    "name": "Devon Bleibtrey",
                    "email": "devon@sagebrew.com"
                }
            ]
        }
        m.get(self.intercom_url, json=intercom_mock_data,
              status_code=status.HTTP_200_OK)
        customer_mock_data = {
            "email": "success@simulator.amazonses.com"
        }
        m.get("https://api.stripe.com/v1/customers/cus_00000000000000",
              json=customer_mock_data, status_code=status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000",
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "customer": "cus_00000000000000"
                }
            }
        }
        m.post("https://api.intercom.io/messages/",
               status_code=status.HTTP_202_ACCEPTED)
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['from_user'],
                         ["69989 is not a valid admin ID"])

    @requests_mock.mock()
    def test_valid_event_invalid_customer_request(self, m):
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
            "id": "evt_00000000000000",
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "customer": "cus_00000000000000"
                }
            }
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @requests_mock.mock()
    def test_valid_event_request_account_updated(self, m):
        self.quest.account_verified = "unverified"
        self.quest.save()
        cache.clear()
        account_mock_data = {
            "email": "success@simulator.amazonses.com",
            "verification": {
                "disabled_reason": "fields_needed",
                "due_by": None,
                "fields_needed": ["legal_entity.type"]
            },
            "legal_entity": {
                "verification": {
                    "status": "verified",
                    "details": "Identity document is too unclear to read."
                }
            }
        }
        m.get("https://api.stripe.com/v1/accounts/acct_00000000000000",
              json=account_mock_data, status_code=status.HTTP_200_OK)

        admin_mock_data = {
            "type": "admin.list",
            "admins": [
                {
                    "type": "admin",
                    "id": settings.INTERCOM_ADMIN_ID_DEVON,
                    "name": "Devon Bleibtrey",
                    "email": "devon@sagebrew.com"
                }
            ]
        }
        m.get("https://api.intercom.io/admins", json=admin_mock_data,
              status_code=status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000",
            "type": "account.updated",
            "data": {
                "object": {
                    "id": "acct_00000000000000"
                }
            }
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], "Account Updated")

    @requests_mock.mock()
    def test_no_user_account_updated(self, m):
        account_mock_data = {
            "email": "success@simulator.amazonses.com",
            "verification": {
                "disabled_reason": "fields_needed",
                "due_by": None,
                "fields_needed": ["legal_entity.type"]
            },
            "legal_entity": {
                "verification": {
                    "status": "verified",
                    "details": "Identity document is too unclear to read."
                }
            }
        }
        m.get("https://api.stripe.com/v1/accounts/acct_00000000000000",
              json=account_mock_data, status_code=status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000",
            "type": "account.updated",
            "data": {
                "object": {
                    "id": "acct_00000000000000"
                }
            }
        }
        query = 'MATCH (pleb:Pleb {email: "%s"})-[r]-() ' \
                'DELETE pleb, r' % "success@simulator.amazonses.com"
        db.cypher_query(query)
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['id'], "evt_00000000000000")

    @requests_mock.mock()
    def test_valid_event_request_account_updated_invalid_account(self, m):
        self.quest.account_verified = "unverified"
        self.quest.save()
        cache.clear()
        account_mock_data = {
            "email": "success@simulator.amazonses.com",
            "verification": {
                "disabled_reason": None,
                "due_by": None,
                "fields_needed": []
            },
            "legal_entity": {
                "verification": {
                    "status": "verified",
                    "details": "Identity document is too unclear to read."
                }
            }
        }
        m.get("https://api.stripe.com/v1/accounts/acct_00000000000001",
              json=account_mock_data, status_code=status.HTTP_200_OK)

        admin_mock_data = {
            "type": "admin.list",
            "admins": [
                {
                    "type": "admin",
                    "id": settings.INTERCOM_ADMIN_ID_DEVON,
                    "name": "Devon Bleibtrey",
                    "email": "devon@sagebrew.com"
                }
            ]
        }
        m.get("https://api.intercom.io/admins", json=admin_mock_data,
              status_code=status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000",
            "type": "account.updated",
            "data": {
                "object": {
                    "id": "acct_00000000000001"
                }
            }
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @requests_mock.mock()
    def test_valid_event_request_account_updated_deleted(self, m):
        self.quest.account_verified = "unverified"
        self.quest.save()
        cache.clear()
        account_mock_data = {
            "id": "acct_00000000000000",
            "deleted": True
        }
        m.get("https://api.stripe.com/v1/accounts/acct_00000000000000",
              json=account_mock_data, status_code=status.HTTP_200_OK)
        admin_mock_data = {
            "type": "admin.list",
            "admins": [
                {
                    "type": "admin",
                    "id": settings.INTERCOM_ADMIN_ID_DEVON,
                    "name": "Devon Bleibtrey",
                    "email": "devon@sagebrew.com"
                }
            ]
        }
        m.get("https://api.intercom.io/admins", json=admin_mock_data,
              status_code=status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000",
            "type": "account.updated",
            "data": {
                "object": {
                    "id": "acct_00000000000000"
                }
            }
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @requests_mock.mock()
    def test_valid_event_request_transfer_failed_stripe_account(self, m):
        self.quest.account_verified = "unverified"
        self.quest.save()
        cache.clear()
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
              json=account_mock_data, status_code=status.HTTP_201_CREATED)
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000",
            "type": "transfer.failed",
            "data": {
                "object": {
                    "id": "tr_00000000000000"
                }
            }
        }
        intercom_mock_data = {
            "event_name": "stripe-transfer-failed",
            "user_id": self.pleb.username,
            "created": calendar.timegm(datetime.now(pytz.utc).utctimetuple())
        }
        m.post("https://api.intercom.io/events/", json=intercom_mock_data,
               status_code=status.HTTP_202_ACCEPTED)
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], "Transfer Failed")

    @requests_mock.mock()
    def test_no_user_transfer_failed_stripe_account(self, m):
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
              json=account_mock_data, status_code=status.HTTP_201_CREATED)
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000",
            "type": "transfer.failed",
            "data": {
                "object": {
                    "id": "tr_00000000000000"
                }
            }
        }
        query = 'MATCH (pleb:Pleb {email: "%s"})-[r]-() ' \
                'DELETE pleb, r' % "success@simulator.amazonses.com"
        db.cypher_query(query)
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['id'], "evt_00000000000000")

    @requests_mock.mock()
    def test_valid_event_request_transfer_failed_account_deleted(self, m):
        self.quest.account_verified = "unverified"
        self.quest.save()
        cache.clear()
        transfer_mock_data = {
            "type": "stripe_account",
            "destination": "acct_00000000000000"
        }
        m.get("https://api.stripe.com/v1/transfers/tr_00000000000000",
              json=transfer_mock_data, status_code=status.HTTP_200_OK)
        account_mock_data = {
            "id": "acct_00000000000000",
            "deleted": True
        }
        m.get("https://api.stripe.com/v1/accounts/acct_00000000000000",
              json=account_mock_data, status_code=status.HTTP_201_CREATED)
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000",
            "type": "transfer.failed",
            "data": {
                "object": {
                    "id": "tr_00000000000000"
                }
            }
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, data)

    @requests_mock.mock()
    def test_transfer_failed_stripe_account_invalid_transfer(self, m):
        self.quest.account_verified = "unverified"
        self.quest.save()
        cache.clear()
        transfer_mock_data = {
            "type": "stripe_account",
            "destination": "acct_00000000000000"
        }
        m.get("https://api.stripe.com/v1/transfers/tr_00000000000001",
              json=transfer_mock_data, status_code=status.HTTP_200_OK)
        account_mock_data = {
            "email": "success@simulator.amazonses.com"
        }
        m.get("https://api.stripe.com/v1/accounts/acct_00000000000000",
              json=account_mock_data, status_code=status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000",
            "type": "transfer.failed",
            "data": {
                "object": {
                    "id": "tr_00000000000001"
                }
            }
        }
        intercom_mock_data = {
            "event_name": "stripe-transfer-failed",
            "user_id": self.pleb.username,
            "created": calendar.timegm(datetime.now(pytz.utc).utctimetuple())
        }
        m.post("https://api.intercom.io/events/", json=intercom_mock_data,
               status_code=status.HTTP_202_ACCEPTED)
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @requests_mock.mock()
    def test_valid_event_request_trial_will_end(self, m):
        self.quest.account_verified = "unverified"
        self.quest.save()
        cache.clear()
        customer_mock_data = {
            "email": "success@simulator.amazonses.com"
        }
        m.get("https://api.stripe.com/v1/customers/cus_00000000000000",
              json=customer_mock_data, status_code=status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000",
            "type": "customer.subscription.trial_will_end",
            "data": {
                "object": {
                    "customer": "cus_00000000000000"
                }
            }
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], "Trail Will End")

    @requests_mock.mock()
    def test_no_user_request_trial_will_end(self, m):
        customer_mock_data = {
            "email": "success@simulator.amazonses.com"
        }
        m.get("https://api.stripe.com/v1/customers/cus_00000000000000",
              json=customer_mock_data, status_code=status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000",
            "type": "customer.subscription.trial_will_end",
            "data": {
                "object": {
                    "customer": "cus_00000000000000"
                }
            }
        }
        query = 'MATCH (pleb:Pleb {email: "%s"})-[r]-() ' \
                'DELETE pleb, r' % "success@simulator.amazonses.com"
        db.cypher_query(query)
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['id'], "evt_00000000000000")

    @requests_mock.mock()
    def test_valid_event_request_trial_will_end_invalid_customer(self, m):
        self.quest.account_verified = "unverified"
        self.quest.save()
        cache.clear()
        customer_mock_data = {
            "email": "success@simulator.amazonses.com"
        }
        m.get("https://api.stripe.com/v1/customers/cus_00000000000001",
              json=customer_mock_data, status_code=status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000",
            "type": "customer.subscription.trial_will_end",
            "data": {
                "object": {
                    "customer": "cus_00000000000001"
                }
            }
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @requests_mock.mock()
    def test_invalid_event_type(self, m):
        self.quest.account_verified = "unverified"
        self.quest.save()
        cache.clear()
        self.client.force_authenticate(user=self.user)
        url = reverse('accounting-list')
        data = {
            "id": "evt_00000000000000",
            "type": "some.invalid.thing",
            "data": {
                "object": {
                    "customer": "cus_00000000000001"
                }
            }
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
