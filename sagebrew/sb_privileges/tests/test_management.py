import logging
from json import loads
from django.conf import settings
from django.test import TestCase
from django.core.management import call_command

from sb_privileges.neo_models import Privilege, Restriction, SBAction
from sb_requirements.neo_models import Requirement

logger = logging.getLogger('loggly_logs')


class TestCreatePrivileges(TestCase):
    def test_create_privileges(self):
        call_command('create_privileges')
        with open('%s/sb_privileges/management/commands'
                  '/privilege_nodes.json' % settings.PROJECT_DIR,
                  'r') as data_file:
            data = loads(data_file.read())
            for privilege in data['privileges']:
                requirements = privilege.pop('requirements', [])
                actions = privilege.pop('actions', [])
                privilege_obj = Privilege.nodes.get(name=privilege["name"])
                self.assertIsNotNone(privilege_obj)
                for requirement in requirements:
                    requirement_obj = Requirement.nodes.get(
                        name=requirement["name"])
                    self.assertIsNotNone(requirement_obj)
                for action in actions:
                    action_obj = SBAction.nodes.get(action=action["permission"])
                    self.assertIsNotNone(action_obj)
                for restriction in data['restrictions']:
                    restrict_obj = Restriction.nodes.get(
                        name=restriction["name"])
                    self.assertIsNotNone(restrict_obj)
