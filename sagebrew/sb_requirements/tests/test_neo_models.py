import requests_mock

from django.test import TestCase
from django.contrib.auth.models import User

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test


class TestRequirementModel(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_equal_operator_pass(self):
        pass

    def test_equal_operator_fail(self):
        pass

    def test_equal_operator_invalid(self):
        pass

    def test_less_than_equal_operator_pass(self):
        pass

    def test_less_than_equal_operator_fail(self):
        pass

    def test_less_than_equal_operator_invalid(self):
        pass

    def test_less_than_operator_pass(self):
        pass

    def test_less_than_operator_fail(self):
        pass

    def test_less_than_operator_invalid(self):
        pass

    def test_greater_than_equal_operator_pass(self):
        pass

    def test_greater_than_equal_operator_fail(self):
        pass

    def test_greater_than_equal_operator_invalid(self):
        pass

    def test_greater_than_operator_pass(self):
        pass

    def test_greater_than_operator_fail(self):
        pass

    def test_greater_than_operator_invalid(self):
        pass

    def test_not_equal_operator_pass(self):
        pass

    def test_not_equal_operator_fail(self):
        pass

    def test_not_equal_operator_invalid(self):
        pass

    def test_not_operator_pass(self):
        pass

    def test_not_operator_fail(self):
        pass

    def test_not_operator_invalid(self):
        pass

    def test_is_not_operator_pass(self):
        pass

    def test_is_not_operator_fail(self):
        pass

    def test_is_not_operator_invalid(self):
        pass

    def test_is_operator_pass(self):
        pass

    def test_is_operator_fail(self):
        pass

    def test_is_operator_invalid(self):
        pass

    def test_truth_operator_pass(self):
        pass

    def test_truth_operator_fail(self):
        pass

    def test_truth_operator_invalid(self):
        pass

    @requests_mock.mock()
    def test_server_connection_error(self):
        pass

    def test_non_json_response(self):
        pass

    def test_invalid_key(self):
        # May want to just raise rather than return the exception
        pass

    def test_malicious_operator(self):
        pass

    def test_username_url(self):
        pass
