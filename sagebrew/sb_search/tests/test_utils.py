from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_search.utils import process_search_result
from sb_registration.utils import create_user_util_test

class TestProcessSearchResultUtil(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_process_search_result_question(self):
        my_dict = {
            '_source': {
                'sb_score': 100,
                'object_uuid': str(uuid1()),
                'related_user': 'tylerwiersing',
            },
            '_type': 'sb_questions.neo_models.SBQuestion',
            '_score': .92,
            '_id': str(uuid1()),
            '_index': 'full-search-base'
        }

        self.assertNotEqual(process_search_result(my_dict), {})

    def test_process_search_result_pleb(self):
        my_dict = {
            '_source': {
                'sb_score': 100,
                'object_uuid': str(uuid1()),
                'related_user': 'tylerwiersing',
            },
            '_type': 'pleb',
            '_score': .92,
            '_id': str(uuid1()),
            '_index': 'full-search-base'
        }
        self.assertNotEqual(process_search_result(my_dict), {})