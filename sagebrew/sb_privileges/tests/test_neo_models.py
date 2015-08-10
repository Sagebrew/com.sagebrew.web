import requests_mock

from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework import status

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_requirements.neo_models import Requirement
from sb_privileges.neo_models import Privilege


class TestRequirementModel(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.api_endpoint = "http://www.sagebrew.com/v1"

    @requests_mock.mock()
    def test_achieve_privilege(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"reputation": 0}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Total Rep 0 Priv Test",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="reputation", operator='coperator\neq\np0\n.', condition=0)
        req.save()
        privilege = Privilege(name="Awesome Privilege")
        privilege.save()
        privilege.requirements.connect(req)
        result = privilege.check_requirements(self.pleb)
        privilege.requirements.disconnect(req)
        privilege.delete()
        req.delete()
        self.assertTrue(result)

    @requests_mock.mock()
    def test_do_not_get_privilege(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"reputation": 10}, status_code=status.HTTP_200_OK)
        req = Requirement(
            name="Total Rep 0 Priv Test",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="reputation", operator='coperator\neq\np0\n.', condition=0)
        req.save()
        privilege = Privilege(name="Awesome Privilege")
        privilege.save()
        privilege.requirements.connect(req)
        result = privilege.check_requirements(self.pleb)
        privilege.requirements.disconnect(req)
        privilege.delete()
        req.delete()
        self.assertFalse(result)

    @requests_mock.mock()
    def test_do_not_get_privilege_bad_request(self, m):
        m.get('%s/profiles/%s/reputation/' % (
            self.api_endpoint, self.pleb.username),
            json={"reputation": 0}, status_code=status.HTTP_400_BAD_REQUEST)
        req = Requirement(
            name="Total Rep 0 Priv Test",
            url='%s/profiles/<username>/reputation/' % self.api_endpoint,
            key="reputation", operator='coperator\neq\np0\n.', condition=0)
        req.save()
        privilege = Privilege(name="Awesome Privilege")
        privilege.save()
        privilege.requirements.connect(req)
        try:
            privilege.check_requirements(self.pleb)
        except IOError as e:
            privilege.requirements.disconnect(req)
            privilege.delete()
            req.delete()
            self.assertIsInstance(e, IOError)
            self.assertEqual(str(e), '400')
