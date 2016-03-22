import time
import requests_mock
from uuid import uuid1

from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from django.core.cache import cache

from rest_framework import status
from rest_framework.test import APITestCase

from neomodel import db

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_privileges.neo_models import SBAction, Privilege
from sb_privileges.utils import create_privilege, manage_privilege_relation
from sb_requirements.neo_models import Requirement


class TestManagePrivilegeRelation(APITestCase):

    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        db.cypher_query(query)
        cache.clear()
        self.email = "success@simulator.amazonses.com"
        self.password = "testpassword"
        res = create_user_util_test(self.email, task=True)
        while not res['task_id'].ready():
            time.sleep(.1)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.privilege_name = str(uuid1())
        self.privilege = Privilege(name=self.privilege_name).save()
        self.requirement = Requirement(name=str(uuid1()),
                                       url=settings.WEB_ADDRESS +
                                       "/v1/profiles/"
                                       "<username>/reputation/",
                                       key="reputation",
                                       operator="coperator\nge\np0\n.",
                                       condition=30).save()
        self.action = SBAction(resource=str(uuid1()),
                               url="/v1/comments/").save()
        self.privilege.actions.connect(self.action)
        self.action.privilege.connect(self.privilege)
        self.test_url = settings.WEB_ADDRESS
        self.privilege.requirements.connect(self.requirement)

    def test_no_privileges(self):
        for privilege in Privilege.nodes.all():
            privilege.delete()

        response = manage_privilege_relation(username=self.username)
        self.assertTrue(response)

    @requests_mock.mock()
    def test_check_privleges(self, m):
        self.client.force_authenticate(user=self.user)
        m.get("%s/v1/profiles/%s/reputation/" % (self.test_url,
                                                 self.user.username),
              json={"reputation": 50}, status_code=status.HTTP_200_OK)
        response = manage_privilege_relation(username=self.username)
        self.assertTrue(response)

    @requests_mock.mock()
    def test_dont_gain_privilege(self, m):
        self.client.force_authenticate(user=self.user)
        m.get("%s/v1/profiles/%s/reputation/" % (self.test_url,
                                                 self.user.username),
              json={"reputation": 25}, status_code=status.HTTP_200_OK)
        response = manage_privilege_relation(username=self.username)
        self.assertTrue(response)

    @requests_mock.mock()
    def test_lose_privilege(self, m):
        self.client.force_authenticate(user=self.user)
        m.get("%s/v1/profiles/%s/reputation/" % (self.test_url,
                                                 self.user.username),
              json={"reputation": 50}, status_code=status.HTTP_200_OK)
        manage_privilege_relation(username=self.username)
        m.get("%s/v1/profiles/%s/reputation/" % (self.test_url,
                                                 self.user.username),
              json={"reputation": 25}, status_code=status.HTTP_200_OK)
        response = manage_privilege_relation(username=self.username)
        self.assertTrue(response)

    @requests_mock.mock()
    def test_lose_and_regain_privilege(self, m):
        self.client.force_authenticate(user=self.user)
        m.get("%s/v1/profiles/%s/reputation/" % (self.test_url,
                                                 self.user.username),
              json={"reputation": 50}, status_code=status.HTTP_200_OK)
        manage_privilege_relation(username=self.username)
        m.get("%s/v1/profiles/%s/reputation/" % (self.test_url,
                                                 self.user.username),
              json={"reputation": 25}, status_code=status.HTTP_200_OK)
        manage_privilege_relation(username=self.username)
        m.get("%s/v1/profiles/%s/reputation/" % (self.test_url,
                                                 self.user.username),
              json={"reputation": 50}, status_code=status.HTTP_200_OK)
        response = manage_privilege_relation(username=self.username)
        self.assertTrue(response)


class TestCreatePrivilege(TestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.password = "testpassword"
        res = create_user_util_test(self.email, task=True)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.privilege = Privilege(name=str(uuid1())).save()
        self.requirement = Requirement(name=str(uuid1()),
                                       url=settings.WEB_ADDRESS +
                                       "/v1/profiles/"
                                       "<username>/reputation/",
                                       key="reputation",
                                       operator="coperator\nge\np0\n.",
                                       condition=0).save()
        self.privilege.requirements.connect(self.requirement)

    def test_create_privilege(self):
        action = SBAction(resource="intercom", permission="write").save()
        privilege_data = {
            "name": "this is a test privilege"
        }
        actions = [{'object_uuid': action.object_uuid}]
        requirements = [{'object_uuid': self.requirement.object_uuid}]
        res = create_privilege(privilege_data, actions, requirements)
        self.assertTrue(res)

    def test_create_privilege_action_does_not_exist(self):
        privilege_data = {
            "name": "this is a test privilege"
        }
        actions = [{'object_uuid': "this doesnt exist"}]
        requirements = [{'object_uuid': self.requirement.object_uuid}]
        res = create_privilege(privilege_data, actions, requirements)
        self.assertIsInstance(res, Exception)

    def test_create_privilege_requirement_does_not_exist(self):
        action = SBAction(resource="intercom", permission="write").save()
        privilege_data = {
            "name": "this is a test privilege"
        }
        actions = [{'object_uuid': action.object_uuid}]
        requirements = [{'object_uuid': "this doesnt exist"}]
        res = create_privilege(privilege_data, actions, requirements)
        self.assertIsInstance(res, Exception)
