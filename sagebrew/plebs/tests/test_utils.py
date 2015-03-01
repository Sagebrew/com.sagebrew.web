from os import environ
from subprocess import check_call
import pickle
from django.test import TestCase
from django.contrib.auth.models import User
from neomodel.exception import DoesNotExist

from api.utils import wait_util
from plebs.neo_models import Pleb
from plebs.utils import prepare_user_search_html
from sb_registration.utils import create_user_util_test


class TestPrepareUserSearchHTML(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"

        self.password = "testpassword"
        res = create_user_util_test(self.email)
        self.username = res["username"]
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

    def test_connection_refused(self):
        check_call("sudo service neo4j-service stop", shell=True)
        res = prepare_user_search_html(self.user.email)
        check_call("sudo nohup service neo4j-service start > "
                   "%s/neo4j_logs.log &" % environ.get("CIRCLE_ARTIFACTS",
                                                       "/home/ubuntu/"),
                   shell=True)
        self.assertIsNone(res)


class TestPleb(TestCase):
    def test_pickle_does_not_exist(self):
        try:
            from_citizen = Pleb.nodes.get(email="notanemail@example.com")
        except(Pleb.DoesNotExist, DoesNotExist) as e:
            pickle_instance = pickle.dumps(e)
            self.assertTrue(pickle_instance)
            self.assertTrue(pickle.loads(pickle_instance))