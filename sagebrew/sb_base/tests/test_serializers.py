import requests_mock
from uuid import uuid1

from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from neomodel import db

from sb_registration.utils import create_user_util_test

from sb_base.serializers import (IntercomMessageSerializer,
                                 IntercomEventSerializer,
                                 VotableContentSerializer)
from sb_questions.neo_models import Question
from sb_solutions.neo_models import Solution
from sb_comments.neo_models import Comment
from sb_quests.neo_models import Quest
from sb_missions.neo_models import Mission


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
                    "id": 69989,
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
                    "id": 69989,
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
                    "id": 69989,
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
                    "id": 69989,
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
                    "id": 69989,
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


class IntercomEventSerializerTests(APITestCase):

    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        db.cypher_query(query)
        self.unit_under_test_name = 'accounting'
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)

    def test_valid_message_no_meta(self):
        event_data = {
            'event_name': 'signup-no-mission',
            'username': self.pleb.username,
        }
        serializer = IntercomEventSerializer(data=event_data)
        serializer.is_valid()
        serializer.save()
        self.assertEqual(serializer.data['event_name'], 'signup-no-mission')
        self.assertEqual(serializer.data['username'], self.pleb.username)

    def test_valid_message_with_meta(self):
        event_data = {
            'event_name': 'signup-no-mission',
            'username': self.pleb.username,
            'metadata': {
                "hello": "world"
            }
        }
        serializer = IntercomEventSerializer(data=event_data)
        serializer.is_valid()
        serializer.save()
        self.assertEqual(serializer.data['event_name'], 'signup-no-mission')
        self.assertEqual(serializer.data['username'], self.pleb.username)
        self.assertEqual(serializer.data['metadata']['hello'], "world")

    def test_user_does_not_exist(self):
        event_data = {
            'event_name': 'signup-no-mission',
            'username': "haha got you",
            'metadata': {
                "hello": "world"
            }
        }
        serializer = IntercomEventSerializer(data=event_data)
        serializer.is_valid()
        self.assertEqual(serializer.errors['username'],
                         ['Does not exist in the database.'])


class VotableContentSerializerTests(APITestCase):

    def setUp(self):
        self.unit_under_test_name = 'comment'
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.comment = Comment(content="test comment",
                               owner_username=self.pleb.username).save()
        self.comment.owned_by.connect(self.pleb)

    def test_get_can_comment_mission_owner(self):
        quest = Quest(owner_username=self.pleb.username).save()
        quest.owner.connect(self.pleb)
        mission = Mission(owner_username=self.pleb.username).save()
        quest.missions.connect(mission)
        question = Question(content='test content title',
                            title=str(uuid1())).save()
        mission.associated_with.connect(question)
        factory = APIRequestFactory()
        request = factory.get('')
        request.user = self.user
        res = VotableContentSerializer(
            question, context={'request': request}).data
        self.assertTrue(res['can_comment']['status'])
        mission.delete()
        quest.delete()

    def test_get_can_flag_mission_owner(self):
        quest = Quest(owner_username=self.pleb.username).save()
        quest.owner.connect(self.pleb)
        mission = Mission(owner_username=self.pleb.username).save()
        quest.missions.connect(mission)
        question = Question(content='test content title',
                            title=str(uuid1())).save()
        mission.associated_with.connect(question)
        factory = APIRequestFactory()
        request = factory.get('')
        request.user = self.user
        res = VotableContentSerializer(
            question, context={'request': request}).data
        self.assertTrue(res['can_flag']['status'])
        mission.delete()
        quest.delete()

    def test_get_can_flag_comment_mission_owner(self):
        quest = Quest(owner_username=self.pleb.username).save()
        quest.owner.connect(self.pleb)
        mission = Mission(owner_username=self.pleb.username).save()
        quest.missions.connect(mission)
        question = Question(content='test content title',
                            title=str(uuid1())).save()
        mission.associated_with.connect(question)
        question.comments.connect(self.comment)
        self.comment.parent_type = "question"
        self.comment.parent_id = question.object_uuid
        self.comment.owner_username = "random_test_username"
        self.comment.save()
        factory = APIRequestFactory()
        request = factory.get('')
        request.user = self.user
        res = VotableContentSerializer(
            self.comment, context={'request': request}).data
        self.assertTrue(res['can_flag']['status'])
        mission.delete()
        quest.delete()
        self.comment.owner_username = self.pleb.username
        self.comment.save()

    def test_get_can_downvote_mission_owner(self):
        quest = Quest(owner_username=self.pleb.username).save()
        quest.owner.connect(self.pleb)
        mission = Mission(owner_username=self.pleb.username).save()
        quest.missions.connect(mission)
        question = Question(content='test content title',
                            title=str(uuid1())).save()
        mission.associated_with.connect(question)
        factory = APIRequestFactory()
        request = factory.get('')
        request.user = self.user
        res = VotableContentSerializer(
            question, context={'request': request}).data
        self.assertTrue(res['can_downvote']['status'])
        mission.delete()
        quest.delete()

    def test_get_can_downvote_comment_mission_owner(self):
        quest = Quest(owner_username=self.pleb.username).save()
        quest.owner.connect(self.pleb)
        mission = Mission(owner_username=self.pleb.username).save()
        quest.missions.connect(mission)
        question = Question(content='test content title',
                            title=str(uuid1())).save()
        mission.associated_with.connect(question)
        question.comments.connect(self.comment)
        self.comment.parent_type = "question"
        self.comment.parent_id = question.object_uuid
        self.comment.owner_username = "random_test_username"
        self.comment.save()
        factory = APIRequestFactory()
        request = factory.get('')
        request.user = self.user
        res = VotableContentSerializer(
            self.comment, context={'request': request}).data
        self.assertTrue(res['can_flag']['status'])
        mission.delete()
        quest.delete()
        self.comment.owner_username = self.pleb.username
        self.comment.save()
