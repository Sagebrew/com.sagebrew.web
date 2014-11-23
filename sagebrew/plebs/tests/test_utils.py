import shortuuid
from os import environ
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from plebs.neo_models import Pleb
from plebs.utils import prepare_user_search_html
from sb_registration.utils import create_user_util

class TestPrepareUserSearchHTML(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.username = shortuuid.uuid()
        self.password = "testpassword"
        res = create_user_util("test", "test", self.email, self.password,
                               self.username)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_prepare_user_search_html_success(self):
        res = prepare_user_search_html(self.user.email)

        self.assertIn('<div style="font-weight: bold">Reputation: 0 | '
                      'Mutual Friends: 0</div>', res)

    def test_prepare_user_pleb_does_not_exist(self):
        res = prepare_user_search_html("fake_email@fakegoogle.com")
        self.assertFalse(res)

    def test_cypher_exception(self):
        temp_neo = environ['NEO4J_REST_URL']
        environ['NEO4J_REST_URL'] = "http://sagebrew.com:7474/db/data/"
        res = prepare_user_search_html(self.user.email)
        environ["NEO4J_REST_URL"] = temp_neo
        
        self.assertIsNone(res)
