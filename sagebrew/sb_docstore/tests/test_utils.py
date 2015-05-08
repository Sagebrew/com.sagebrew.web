import pytz
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_docstore.utils import (add_object_to_table,
                               get_vote, update_vote, get_vote_count,
                               get_user_updates)


class TestDocstoreUtils(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_get_vote(self):
        uuid = str(uuid1())
        now = unicode(datetime.now(pytz.utc))
        vote_data = {
            'parent_object': uuid,
            'user': self.pleb.username,
            'status': 1,
            'created': now
        }
        res = add_object_to_table('votes', vote_data)
        self.assertTrue(res)

        res = get_vote(uuid, self.pleb.username)

        self.assertNotEqual(res, False)
        self.assertFalse(isinstance(res, Exception))

    def test_update_vote(self):
        uuid = str(uuid1())
        now = unicode(datetime.now(pytz.utc))
        vote_data = {
            'parent_object': uuid,
            'user': self.pleb.username,
            'status': 1,
            'created': now
        }
        res = add_object_to_table('votes', vote_data)
        self.assertTrue(res)

        res = update_vote(uuid, self.pleb.username, 0, now)
        self.assertNotEqual(res, False)
        self.assertFalse(isinstance(res, Exception))

    def test_get_vote_count(self):
        uuid = str(uuid1())
        now = unicode(datetime.now(pytz.utc))
        vote_data = {
            'parent_object': uuid,
            'user': self.pleb.username,
            'status': 1,
            'created': now
        }
        res = add_object_to_table('votes', vote_data)
        self.assertTrue(res)

        res = get_vote_count(uuid, 1)

        self.assertEqual(res, 1)

    def test_get_user_updates(self):
        res = get_user_updates(self.pleb.username, str(uuid1()), 'votes')

        self.assertIsInstance(res, dict)
