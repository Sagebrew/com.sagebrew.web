from uuid import uuid1

import pickle
from django.test import TestCase
from django.contrib.auth.models import User
from neomodel.exception import DoesNotExist

from api.utils import wait_util
from plebs.neo_models import Pleb, FriendRequest
from plebs.utils import prepare_user_search_html, create_friend_request_util
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
        res = prepare_user_search_html(self.user.username)
        self.assertIn('<div class="col-lg-4 col-md-5 col-sm-4 col-xs-4">', res)

    def test_prepare_user_pleb_does_not_exist(self):
        res = prepare_user_search_html("fake_email@fakegoogle.com")
        self.assertFalse(res)
# TODO add this back in
'''
    Until we have a stable version of Neo4J in circle and everywhere else
    on our machines and aren't working with SaaS for some instances of Neo
    I'm commenting this out. We've proved out the functionality with the current
    iterations of py2neo 1.6.x, neomodel 1.x, and neo4j 2.1.x.
    def test_connection_refused(self):
        check_call("sudo service neo4j-service stop", shell=True)
        res = prepare_user_search_html(self.user.username)
        if environ.get("CIRCLECI", "false") == "true":
            check_call("sudo nohup service neo4j-service start > "
                       "%s/neo4j_logs.log &" % environ.get("CIRCLE_ARTIFACTS",
                                                           "/home/logs"),
                       shell=True)
            self.assertIsNone(res)
'''

class TestPleb(TestCase):
    def test_pickle_does_not_exist(self):
        try:
            from_citizen = Pleb.nodes.get(email="notanemail@example.com")
        except(Pleb.DoesNotExist, DoesNotExist) as e:
            pickle_instance = pickle.dumps(e)
            self.assertTrue(pickle_instance)
            self.assertTrue(pickle.loads(pickle_instance))


class TestCreateFriendRequestUtil(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb1 = Pleb.nodes.get(email=self.email)
        self.user1 = User.objects.get(email=self.email)
        self.email2= "bounce@simulator.amazonses.com"
        res = create_user_util_test(self.email2)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb2 = Pleb.nodes.get(email=self.email2)
        self.user2 = User.objects.get(email=self.email2)

    def test_create_friend_request_util_success(self):
        res = create_friend_request_util(self.pleb1.username,
                                         self.pleb2.username,
                                         str(uuid1()))

        self.assertTrue(res)

    def test_create_friend_request_util_success_already_sent(self):
        friend_request = FriendRequest(object_uuid=str(uuid1()))
        friend_request.save()
        self.pleb1.friend_requests_sent.connect(friend_request)
        self.pleb2.friend_requests_received.connect(friend_request)
        friend_request.request_to.connect(self.pleb2)
        friend_request.request_from.connect(self.pleb1)

        res = create_friend_request_util(self.pleb1.username,
                                         self.pleb2.username,
                                         str(uuid1()))

        self.assertTrue(res)

    def test_create_friend_request_util_fail_pleb_does_not_exist(self):
        res = create_friend_request_util(from_username=self.pleb1.username,
                                         to_username=str(uuid1()),
                                         object_uuid=str(uuid1()))

        self.assertIsInstance(res, DoesNotExist)

    def test_create_friend_request_util_fail_pleb_does_not_exist_pickle(self):
        res = create_friend_request_util(from_username=self.pleb1.username,
                                         to_username=str(uuid1()),
                                         object_uuid=str(uuid1()))
        pickle_instance = pickle.dumps(res)
        self.assertTrue(pickle_instance)
        self.assertTrue(pickle.loads(pickle_instance))
