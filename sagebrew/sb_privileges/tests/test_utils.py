import logging
from json import loads
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from neomodel.exception import DoesNotExist

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_privileges.neo_models import SBPrivilege, SBRestriction, SBAction
from sb_requirements.neo_models import SBRequirement
from sb_registration.utils import create_user_util_test

from sb_privileges.utils import manage_privilege_relation

logger = logging.getLogger('loggly_logs')


class TestManagePrivilegeRelation(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"

        self.password = "testpassword"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_manage_privilege_relation(self):
        result = manage_privilege_relation(self.username)
        self.assertTrue(result)
'''
    def test_manage_privilege_relation_no_pleb(self):
        result = manage_privilege_relation("hello_there")
        self.assertIsInstance(result, Exception)

    def test_pleb_already_has_privilege(self):
        result = manage_privilege_relation(self.username)
        self.assertTrue(result)
'''