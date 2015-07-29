from uuid import uuid1

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_privileges.neo_models import SBAction, Privilege
from sb_privileges.utils import manage_privilege_relation, create_privilege
from sb_requirements.neo_models import Requirement


class TestManagePrivilegeRelation(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.password = "testpassword"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.privilege = Privilege().save()
        self.requirement = Requirement(name=str(uuid1()),
                                       url=settings.WEB_ADDRESS +
                                       "/v1/profiles/"
                                       "<username>/reputation/",
                                       key="reputation",
                                       operator="coperator\nge\np0\n.",
                                       condition=0).save()
        self.privilege.requirements.connect(self.requirement)

    def test_manage_privilege_relation_no_pleb(self):
        result = manage_privilege_relation("hello_there")
        self.assertIsInstance(result, Exception)

    def test_pleb_already_has_privilege(self):
        result = manage_privilege_relation(self.username)
        self.assertTrue(result)


class TestCreatePrivilege(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.password = "testpassword"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.privilege = Privilege().save()
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
