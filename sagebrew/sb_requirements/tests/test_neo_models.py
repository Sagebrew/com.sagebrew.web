import requests_mock

from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework import status

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_requirements.neo_models import Requirement


class TestRequirementModel(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.api_endpoint = "http://www.sagebrew.com/v1"

    @requests_mock.mock()
    def test_equal_operator_pass(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"reputation": 0}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Total Rep 0",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="reputation", operator='coperator\neq\np0\n.', condition=0)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertTrue(result['response'])
        self.assertEqual(result['operator'], 'equal to')
        self.assertEqual(result['detail'], 'The requirement Total Rep 0 was '
                                           'met')
        self.assertEqual(result['key'], 'reputation')
        req.delete()

    @requests_mock.mock()
    def test_equal_operator_pass_string(self, m):
        m.get('%s/profiles/%s/testing/' % (
            self.api_endpoint, self.pleb.username),
            json={"test": "hello"}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Total Rep 0",
            url='%s/profiles/<username>/testing/' % self.api_endpoint,
            key="test", operator='coperator\neq\np0\n.',
            condition="hello")
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertTrue(result['response'])
        req.delete()

    @requests_mock.mock()
    def test_equal_operator_fail(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"reputation": 5}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Total Rep 0",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="reputation", operator='coperator\neq\np0\n.', condition=0)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertFalse(result['response'])
        self.assertEqual(result['operator'], 'equal to')
        self.assertEqual(result['detail'], 'You have 5 reputation, reputation '
                                           'must be equal to 0 to gain the '
                                           'Total Rep 0 Privilege.')
        self.assertEqual(result['key'], 'reputation')
        req.delete()

    @requests_mock.mock()
    def test_equal_operator_fail_string(self, m):
        m.get('%s/profiles/%s/testing/' % (
            self.api_endpoint, self.pleb.username),
            json={"test": "goodbye"}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Total Rep 0",
            url='%s/profiles/<username>/testing/' % self.api_endpoint,
            key="test", operator='coperator\neq\np0\n.',
            condition="hello")
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertFalse(result['response'])
        req.delete()

    @requests_mock.mock()
    def test_less_than_equal_operator_pass(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"reputation": 10}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="At most 10 Rep",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="reputation", operator='coperator\nle\np0\n.', condition=10)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertTrue(result['response'])
        self.assertEqual(result['operator'], 'at most')
        self.assertEqual(result['detail'], 'The requirement At most 10 Rep'
                                           ' was met')
        self.assertEqual(result['key'], 'reputation')
        req.delete()

    @requests_mock.mock()
    def test_less_than_equal_operator_fail(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"reputation": 15}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="At most 10 Rep",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="reputation", operator='coperator\nle\np0\n.', condition=10)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertFalse(result['response'])
        self.assertEqual(result['operator'], 'at most')
        self.assertEqual(result['detail'], 'You have 15 reputation, '
                                           'reputation must be at most 10 '
                                           'to gain the At most 10 Rep '
                                           'Privilege.')
        self.assertEqual(result['key'], 'reputation')
        req.delete()

    @requests_mock.mock()
    def test_less_than_operator_pass(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"reputation": 5}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Less than 10 Rep",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="reputation", operator='coperator\nlt\np0\n.', condition=10)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertTrue(result['response'])
        self.assertEqual(result['operator'], 'less than')
        self.assertEqual(result['detail'], 'The requirement Less than 10 Rep'
                                           ' was met')
        self.assertEqual(result['key'], 'reputation')
        req.delete()

    @requests_mock.mock()
    def test_less_than_operator_fail(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"reputation": 15}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Less than 10 Rep",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="reputation", operator='coperator\nlt\np0\n.', condition=10)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertFalse(result['response'])
        self.assertEqual(result['operator'], 'less than')
        self.assertEqual(result['detail'], 'You have 15 reputation, '
                                           'reputation must be less than 10 '
                                           'to gain the Less than 10 Rep '
                                           'Privilege.')
        self.assertEqual(result['key'], 'reputation')
        req.delete()

    @requests_mock.mock()
    def test_greater_than_equal_operator_pass(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"reputation": 10}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="At least 10 Rep",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="reputation", operator='coperator\nge\np0\n.', condition=10)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertTrue(result['response'])
        self.assertEqual(result['operator'], 'at least')
        self.assertEqual(result['detail'], 'The requirement At least 10 Rep'
                                           ' was met')
        self.assertEqual(result['key'], 'reputation')
        req.delete()

    @requests_mock.mock()
    def test_greater_than_equal_operator_fail(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"reputation": 5}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="At least 10 Rep",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="reputation", operator='coperator\nge\np0\n.', condition=10)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertFalse(result['response'])
        self.assertEqual(result['operator'], 'at least')
        self.assertEqual(result['detail'], 'You have 5 reputation, '
                                           'reputation must be at least '
                                           '10 to gain the At least 10 '
                                           'Rep Privilege.')
        self.assertEqual(result['key'], 'reputation')
        req.delete()

    @requests_mock.mock()
    def test_greater_than_operator_pass(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"reputation": 15}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="More Than 10 Rep",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="reputation", operator='coperator\ngt\np0\n.', condition=10)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertTrue(result['response'])
        self.assertEqual(result['operator'], 'more than')
        self.assertEqual(result['detail'], 'The requirement More Than 10 Rep '
                                           'was met')
        self.assertEqual(result['key'], 'reputation')
        req.delete()

    @requests_mock.mock()
    def test_greater_than_operator_fail(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"reputation": 10}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="More Than 10 Rep",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="reputation", operator='coperator\ngt\np0\n.', condition=10)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertFalse(result['response'])
        self.assertEqual(result['operator'], 'more than')
        self.assertEqual(result['detail'], 'You have 10 reputation, '
                                           'reputation must be more than '
                                           '10 to gain the More Than 10 '
                                           'Rep Privilege.')
        self.assertEqual(result['key'], 'reputation')
        req.delete()

    @requests_mock.mock()
    def test_not_equal_operator_pass(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"reputation": 15}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Not Equal to 10 Rep",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="reputation", operator='coperator\nne\np0\n.', condition=10)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertTrue(result['response'])
        self.assertEqual(result['operator'], 'not have')
        self.assertEqual(result['detail'], 'The requirement Not Equal to 10 '
                                           'Rep was met')
        self.assertEqual(result['key'], 'reputation')
        req.delete()

    @requests_mock.mock()
    def test_not_equal_operator_pass_string(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"test": "hello"}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Not Equal to 10 Rep",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="test", operator='coperator\nne\np0\n.',
            condition="goodbye")
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertTrue(result['response'])
        self.assertEqual(result['operator'], 'not have')
        self.assertEqual(result['detail'], 'The requirement Not Equal to 10 '
                                           'Rep was met')
        self.assertEqual(result['key'], 'test')
        req.delete()

    @requests_mock.mock()
    def test_not_equal_operator_fail(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"reputation": 10}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Not Equal to 10 Rep",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="reputation", operator='coperator\nne\np0\n.', condition=10)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertFalse(result['response'])
        self.assertEqual(result['operator'], 'not have')
        self.assertEqual(result['detail'], 'You have 10 reputation, '
                                           'reputation must be not have '
                                           '10 to gain the Not Equal to '
                                           '10 Rep Privilege.')
        self.assertEqual(result['key'], 'reputation')
        req.delete()

    @requests_mock.mock()
    def test_not_equal_operator_fail_string(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"test": "hello"}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Not Equal to 10 Rep",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="test", operator='coperator\nne\np0\n.',
            condition="hello")
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertFalse(result['response'])
        self.assertEqual(result['operator'], 'not have')
        self.assertEqual(result['detail'], 'You have hello test, test '
                                           'must be not have hello to gain '
                                           'the Not Equal to 10 Rep '
                                           'Privilege.')
        self.assertEqual(result['key'], 'test')
        req.delete()

    @requests_mock.mock()
    def test_not_operator_pass(self, m):
        m.get('%s/profiles/%s/' % (
            self.api_endpoint, self.pleb.username),
            json={"flag": False}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Flag is False",
            url='%s/profiles/<username>/' % self.api_endpoint,
            key="flag", operator='coperator\nnot_\np0\n.',
            condition=None)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertTrue(result['response'])
        self.assertEqual(result['operator'], 'not')
        self.assertEqual(result['detail'], 'The requirement Flag is False'
                                           ' was met')
        self.assertEqual(result['key'], 'flag')
        req.delete()

    @requests_mock.mock()
    def test_not_operator_pass_none(self, m):
        m.get('%s/profiles/%s/' % (
            self.api_endpoint, self.pleb.username),
            json={"flag": None}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Flag is False",
            url='%s/profiles/<username>/' % self.api_endpoint,
            key="flag", operator='coperator\nnot_\np0\n.')
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertTrue(result['response'])
        self.assertEqual(result['operator'], 'not')
        self.assertEqual(result['detail'], 'The requirement Flag is False'
                                           ' was met')
        self.assertEqual(result['key'], 'flag')
        req.delete()

    @requests_mock.mock()
    def test_not_operator_fail(self, m):
        m.get('%s/profiles/%s/' % (
            self.api_endpoint, self.pleb.username),
            json={"flag": True}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Flag is False",
            url='%s/profiles/<username>/' % self.api_endpoint,
            key="flag", operator='coperator\nnot_\np0\n.',
            condition=None)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertFalse(result['response'])
        self.assertEqual(result['operator'], 'not')
        self.assertEqual(result['detail'], 'You have True flag, flag '
                                           'must be not None to gain the '
                                           'Flag is False Privilege.')
        self.assertEqual(result['key'], 'flag')
        req.delete()

    @requests_mock.mock()
    def test_is_not_operator_pass(self, m):
        m.get('%s/profiles/%s/' % (
            self.api_endpoint, self.pleb.username),
            json={"campaign": "john_apple"}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Quest Subscriber",
            url='%s/profiles/<username>/' % self.api_endpoint,
            key="campaign", operator="coperator\nis_not\np0\n.",
            condition=None)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertTrue(result['response'])
        self.assertEqual(result['operator'], 'is not')
        self.assertEqual(result['detail'], 'The requirement Quest Subscriber'
                                           ' was met')
        self.assertEqual(result['key'], 'campaign')
        req.delete()

    @requests_mock.mock()
    def test_is_not_operator_fail(self, m):
        m.get('%s/profiles/%s/' % (
            self.api_endpoint, self.pleb.username),
            json={"campaign": None}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Quest Subscriber",
            url='%s/profiles/<username>/' % self.api_endpoint,
            key="campaign", operator="coperator\nis_not\np0\n.",
            condition=None)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertFalse(result['response'])
        self.assertEqual(result['operator'], 'is not')
        self.assertEqual(result['detail'], 'You have None campaign, campaign '
                                           'must be is not None to gain the '
                                           'Quest Subscriber Privilege.')
        self.assertEqual(result['key'], 'campaign')
        req.delete()

    @requests_mock.mock()
    def test_is_operator_pass(self, m):
        m.get('%s/profiles/%s/' % (
            self.api_endpoint, self.pleb.username),
            json={"active": True}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Is Active",
            url='%s/profiles/<username>/' % self.api_endpoint,
            key="active", operator='coperator\nis_\np0\n.',
            condition=True)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertTrue(result['response'])
        self.assertEqual(result['operator'], 'is')
        self.assertEqual(result['detail'], 'The requirement Is Active was met')
        self.assertEqual(result['key'], 'active')
        req.delete()

    @requests_mock.mock()
    def test_is_operator_fail(self, m):
        m.get('%s/profiles/%s/' % (
            self.api_endpoint, self.pleb.username),
            json={"active": False}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Is Active",
            url='%s/profiles/<username>/' % self.api_endpoint,
            key="active", operator='coperator\nis_\np0\n.',
            condition=True)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertFalse(result['response'])
        self.assertEqual(result['operator'], 'is')
        self.assertEqual(result['detail'], 'You have False active, active '
                                           'must be is True to gain the Is '
                                           'Active Privilege.')
        self.assertEqual(result['key'], 'active')
        req.delete()

    @requests_mock.mock()
    def test_is_operator_fail_none(self, m):
        m.get('%s/profiles/%s/' % (
            self.api_endpoint, self.pleb.username),
            json={"active": None}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Is Active",
            url='%s/profiles/<username>/' % self.api_endpoint,
            key="active", operator='coperator\nis_\np0\n.',
            condition=True)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertFalse(result['response'])
        self.assertEqual(result['detail'], "We're sorry we cannot check this "
                                           "requirement. We cannot compare a "
                                           "null type in this case. Please "
                                           "try using 'is not' instead.")
        req.delete()

    @requests_mock.mock()
    def test_truth_operator_pass(self, m):
        m.get('%s/profiles/%s/' % (self.api_endpoint, self.pleb.username),
              json={"donations": ["7c8a59a1-847c-42e0-b178-6d1deac01d5f", ]},
              status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Contributor +1",
            url='%s/profiles/<username>/' % self.api_endpoint,
            key="donations", operator="coperator\ntruth\np0\n.",
            condition="[...]")
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertTrue(result['response'])
        self.assertEqual(result['operator'], 'truth')
        self.assertEqual(result['detail'], 'The requirement Contributor +1'
                                           ' was met')
        self.assertEqual(result['key'], 'donations')
        req.delete()

    @requests_mock.mock()
    def test_truth_operator_fail(self, m):
        m.get('%s/profiles/%s/' % (self.api_endpoint, self.pleb.username),
              json={"donations": []},
              status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Contributor +1",
            url='%s/profiles/<username>/' % self.api_endpoint,
            key="donations", operator="coperator\ntruth\np0\n.",
            condition="[...]")
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertFalse(result['response'])
        self.assertEqual(result['operator'], 'truth')
        self.assertEqual(result['detail'], 'You have [] donations, donations '
                                           'must be truth [...] to gain the '
                                           'Contributor +1 Privilege.')
        self.assertEqual(result['key'], 'donations')
        req.delete()

    @requests_mock.mock()
    def test_server_bad_request(self, m):
        m.get('%s/profiles/%s/' % (self.api_endpoint, self.pleb.username),
              json={"donations": []},
              status_code=status.HTTP_400_BAD_REQUEST)
        req = Requirement(
            name="Contributor +1",
            url='%s/profiles/<username>/' % self.api_endpoint,
            key="donations", operator="coperator\ntruth\np0\n.",
            condition="[...]")
        req.save()
        try:
            req.check_requirement(self.user.username)
        except IOError as e:
            self.assertIsInstance(e, IOError)
            self.assertEqual(str(e), '400')
        req.delete()

    @requests_mock.mock()
    def test_server_connection_error(self, m):
        m.get('%s/profiles/%s/' % (self.api_endpoint, self.pleb.username),
              json={"donations": []},
              status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        req = Requirement(
            name="Contributor +1",
            url='%s/profiles/<username>/' % self.api_endpoint,
            key="donations", operator="coperator\ntruth\np0\n.",
            condition="[...]")
        req.save()
        try:
            req.check_requirement(self.user.username)
        except IOError as e:
            self.assertIsInstance(e, IOError)
            self.assertEqual(str(e), '500')
        req.delete()

    @requests_mock.mock()
    def test_non_json_response(self, m):
        m.get('%s/profiles/%s/' % (self.api_endpoint, self.pleb.username),
              text="hello this is not json :)",
              status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Contributor +1",
            url='%s/profiles/<username>/' % self.api_endpoint,
            key="donations", operator="coperator\ntruth\np0\n.",
            condition="[...]")
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertFalse(result['response'])
        self.assertEqual(result['detail'], "We're sorry we cannot check this "
                                           "requirement. It looks like the url "
                                           "you're checking doesn't return "
                                           "a JSON response.")
        req.delete()

    @requests_mock.mock()
    def test_invalid_key(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"badkey": 15}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Not Equal to 10 Rep",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="goodkey", operator='coperator\nne\np0\n.', condition=10)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertFalse(result['response'])
        self.assertEqual(result['detail'], "We're sorry we cannot check "
                                           "this requirement."
                                           " The key cannot be found in the "
                                           "response we received from the "
                                           "server.")
        req.delete()

    @requests_mock.mock()
    def test_non_username_url(self, m):
        m.get('%s/profiles/reputation/' % self.api_endpoint,
              json={"reputation": 0}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Total Rep 0",
            url='%s/profiles/reputation/' % self.api_endpoint,
            key="reputation", operator='coperator\neq\np0\n.', condition=0)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertTrue(result['response'])
        self.assertEqual(result['operator'], 'equal to')
        self.assertEqual(result['detail'], 'The requirement Total Rep 0 was '
                                           'met')
        self.assertEqual(result['key'], 'reputation')
        req.delete()

    @requests_mock.mock()
    def test_invalid_condition(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"reputation": 5}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Total Rep 0",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="reputation", operator='coperator\neq\np0\n.',
            condition="hello")
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertFalse(result['response'])
        self.assertEqual(result['detail'], "We're sorry we cannot check this "
                                           "requirement. The condition is not "
                                           "the same type as the value it's "
                                           "being compared to.")
        req.delete()

    @requests_mock.mock()
    def test_invalid_operator(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"reputation": 5}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Total Rep 0",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="reputation", operator='op\neq\np0\n.',
            condition=0)
        req.save()
        result = req.check_requirement(self.user.username)
        self.assertFalse(result['response'])
        self.assertEqual(result['detail'], "We're sorry we cannot check this "
                                           "requirement. The"
                                           " operator does not seem to be "
                                           "valid.")
        req.delete()
