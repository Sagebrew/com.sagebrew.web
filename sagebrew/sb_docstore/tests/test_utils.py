import pytz
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_docstore.utils import (add_object_to_table, update_doc,
                               get_vote, update_vote, get_vote_count,
                               get_user_updates)


class TestDocstoreUtils(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_update_doc_datetime(self):
        uuid = str(uuid1())
        now = unicode(datetime.now(pytz.utc))
        data = {"parent_object": uuid, "created": now, "user": self.pleb.username,
                "status": 1, "object_uuid": uuid}
        update_data = [{'update_key': 'status', 'update_value': 2}]
        res = add_object_to_table('posts', data)
        self.assertTrue(res)

        res = update_doc('posts', uuid, update_data, uuid, now)

        self.assertFalse(isinstance(res, Exception))

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