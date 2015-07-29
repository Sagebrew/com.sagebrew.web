from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework.test import APIRequestFactory

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_search.utils import (process_search_result)


class TestProcessSearchResult(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_process_search_result_no_sb_score(self):
        data = {
            "_source": {
                "id": str(uuid1()),
            },
            "_type": "question",
            "_score": .97
        }
        res = process_search_result(data)
        self.assertEqual(res['question_uuid'], data['_source']['id'])
        self.assertEqual(res['temp_score'], 0)
        self.assertEqual(res['type'], data['_type'])
        self.assertEqual(res['score'], data['_score'])

    def test_process_search_result_profile(self):
        data = {
            "_source": {
                "id": str(uuid1()),
            },
            "_type": "profile",
            "_score": .97
        }
        res = process_search_result(data)
        self.assertEqual(res['username'], data['_source']['id'])
        self.assertEqual(res['temp_score'], 0)
        self.assertEqual(res['type'], data['_type'])
        self.assertEqual(res['score'], data['_score'])

    def test_process_search_result_campaign(self):
        data = {
            "_source": {
                "id": str(uuid1()),
            },
            "_type": "campaign",
            "_score": .97
        }
        res = process_search_result(data)
        self.assertEqual(res['object_uuid'], data['_source']['id'])
        self.assertEqual(res['temp_score'], 0.97)
        self.assertEqual(res['type'], 'public_official')
        self.assertEqual(res['score'], data['_score'])

    def test_process_search_result_invalid_type(self):
        data = {
            "_source": {
                "id": str(uuid1()),
            },
            "_type": "not_valid_type",
            "_score": .97
        }
        res = process_search_result(data)
        self.assertEqual(res['temp_score'], 0)
