import pytz
from uuid import uuid1
from datetime import datetime
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from django.test import TestCase

from plebs.neo_models import Pleb
from api.utils import wait_util
from sb_registration.utils import create_user_util
from sb_docstore.utils import add_object_to_table

from sb_docstore.views import get_updates_from_dynamo


class TestGetUpdatesFromDynamo(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_get_updates_from_dynamo(self):
        post_id = str(uuid1())
        now = unicode(datetime.now(pytz.utc))

        edit_data = {'parent_object': post_id, 'content': "s;dlkfja;skdjf",
                     'datetime': now, 'user': self.email,
                     'object_type': '1'}
        res = add_object_to_table('edits', edit_data)
        self.assertTrue(res)
        vote_data = {'parent_object': post_id, 'user': self.email,
                     'status': 1, 'datetime': now, 'object_type': '1'}
        res = add_object_to_table('votes', vote_data)
        self.assertTrue(res)
        data = {'object_uuids': [post_id]}
        request = self.factory.post('/docstore/update_neo_api/', data=data,
                                    format='json')
        request.user = self.user

        res = get_updates_from_dynamo(request)

        self.assertEqual(res.status_code, 200)