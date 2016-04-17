import requests_mock
from uuid import uuid1

from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from neomodel import db

from sb_registration.utils import create_user_util_test

from sb_base.serializers import IntercomMessageSerializer


class IntercomMessageSerializerTests(APITestCase):

    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        db.cypher_query(query)
        self.unit_under_test_name = 'accounting'
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.intercom_url = "https://api.intercom.io/admins"

    @requests_mock.mock()
    def test_valid_message(self, m):
        admin_data = {
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
        m.get(self.intercom_url, json=admin_data,
              status_code=status.HTTP_200_OK)
        message_data = {
            'message_type': 'email',
            'subject': 'Subscription Failure Notice',
            'body': "Hi {{ first_name }},\nIt looks like we ran into "
                    "some trouble processing your subscription payment. "
                    "Please verify your billing information is correct "
                    "and we'll automatically retry to process the payment. "
                    "If the payment continues to fail we'll automatically "
                    "move you over to a free account. If you believe "
                    "there has been a mistake please respond to this "
                    "email and we'd be happy to help!\n\nBest Regards,"
                    "\n\nDevon",
            'template': 'personal',
            'from_user': {
                'type': 'admin',
                'id': 69989
            },
            'to_user': {
                'type': 'user',
                'user_id': self.pleb.username
            }
        }
        res = IntercomMessageSerializer(data=message_data)
        self.assertTrue(res.is_valid())

    def test_not_admin_or_user(self):
        message_data = {
            'message_type': 'email',
            'subject': 'Subscription Failure Notice',
            'body': "Hi {{ first_name }},\nIt looks like we ran into "
                    "some trouble processing your subscription payment. "
                    "Please verify your billing information is correct "
                    "and we'll automatically retry to process the payment. "
                    "If the payment continues to fail we'll automatically "
                    "move you over to a free account. If you believe "
                    "there has been a mistake please respond to this "
                    "email and we'd be happy to help!\n\nBest Regards,"
                    "\n\nDevon",
            'template': 'personal',
            'from_user': {
                'type': 'test',
                'id': 69989
            },
            'to_user': {
                'type': 'user',
                'user_id': self.pleb.username
            }
        }
        res = IntercomMessageSerializer(data=message_data)
        valid = res.is_valid()
        self.assertFalse(valid)
        self.assertEqual(
            res.errors,
            {
                'from_user': ["The only valid values for "
                              "'type' are 'user' and 'admin'"]}
        )

    @requests_mock.mock()
    def test_user_id_is_none(self, m):
        admin_data = {
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
        m.get(self.intercom_url, json=admin_data,
              status_code=status.HTTP_200_OK)
        message_data = {
            'message_type': 'email',
            'subject': 'Subscription Failure Notice',
            'body': "Hi {{ first_name }},\nIt looks like we ran into "
                    "some trouble processing your subscription payment. "
                    "Please verify your billing information is correct "
                    "and we'll automatically retry to process the payment. "
                    "If the payment continues to fail we'll automatically "
                    "move you over to a free account. If you believe "
                    "there has been a mistake please respond to this "
                    "email and we'd be happy to help!\n\nBest Regards,"
                    "\n\nDevon",
            'template': 'personal',
            'from_user': {
                'type': 'admin',
                'id': 69989
            },
            'to_user': {
                'type': 'user',
                'id': self.pleb.username
            }
        }
        res = IntercomMessageSerializer(data=message_data)
        valid = res.is_valid()
        self.assertFalse(valid)
        self.assertEqual(
            res.errors,
            {'to_user': ["Must provide the 'user_id' key when attempting "
                         "to send a message to or from a user"]})

    @requests_mock.mock()
    def test_admin_id_is_none(self, m):
        admin_data = {
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
        m.get(self.intercom_url, json=admin_data,
              status_code=status.HTTP_200_OK)
        message_data = {
            'message_type': 'email',
            'subject': 'Subscription Failure Notice',
            'body': "Hi {{ first_name }},\nIt looks like we ran into "
                    "some trouble processing your subscription payment. "
                    "Please verify your billing information is correct "
                    "and we'll automatically retry to process the payment. "
                    "If the payment continues to fail we'll automatically "
                    "move you over to a free account. If you believe "
                    "there has been a mistake please respond to this "
                    "email and we'd be happy to help!\n\nBest Regards,"
                    "\n\nDevon",
            'template': 'personal',
            'from_user': {
                'type': 'admin',
                'user_id': 69989
            },
            'to_user': {
                'type': 'user',
                'user_id': self.pleb.username
            }
        }
        res = IntercomMessageSerializer(data=message_data)
        valid = res.is_valid()
        self.assertFalse(valid)
        self.assertEqual(
            res.errors,
            {'from_user': ["Must provide the 'id' key when attempting to "
                           "send a message to or from an admin"]}
        )

    @requests_mock.mock()
    def test_invalid_admin_id(self, m):
        admin_data = {
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
        m.get(self.intercom_url, json=admin_data,
              status_code=status.HTTP_200_OK)
        message_data = {
            'message_type': 'email',
            'subject': 'Subscription Failure Notice',
            'body': "Hi {{ first_name }},\nIt looks like we ran into "
                    "some trouble processing your subscription payment. "
                    "Please verify your billing information is correct "
                    "and we'll automatically retry to process the payment. "
                    "If the payment continues to fail we'll automatically "
                    "move you over to a free account. If you believe "
                    "there has been a mistake please respond to this "
                    "email and we'd be happy to help!\n\nBest Regards,"
                    "\n\nDevon",
            'template': 'personal',
            'from_user': {
                'type': 'admin',
                'id': 123456
            },
            'to_user': {
                'type': 'user',
                'user_id': self.pleb.username
            }
        }
        res = IntercomMessageSerializer(data=message_data)
        valid = res.is_valid()
        self.assertFalse(valid)
        self.assertEqual(
            res.errors,
            {'from_user': ["123456 is not a valid admin ID"]}
        )

    @requests_mock.mock()
    def test_pleb_doesnt_exist(self, m):
        admin_data = {
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
        m.get(self.intercom_url, json=admin_data,
              status_code=status.HTTP_200_OK)
        message_data = {
            'message_type': 'email',
            'subject': 'Subscription Failure Notice',
            'body': "Hi {{ first_name }},\nIt looks like we ran into "
                    "some trouble processing your subscription payment. "
                    "Please verify your billing information is correct "
                    "and we'll automatically retry to process the payment. "
                    "If the payment continues to fail we'll automatically "
                    "move you over to a free account. If you believe "
                    "there has been a mistake please respond to this "
                    "email and we'd be happy to help!\n\nBest Regards,"
                    "\n\nDevon",
            'template': 'personal',
            'from_user': {
                'type': 'admin',
                'id': 69989
            },
            'to_user': {
                'type': 'user',
                'user_id': str(uuid1())
            }
        }
        res = IntercomMessageSerializer(data=message_data)
        valid = res.is_valid()
        self.assertFalse(valid)
        self.assertEqual(
            res.errors,
            {'to_user':
                ["Profile %s Does Not Exist"
                 % message_data['to_user']['user_id']]})
