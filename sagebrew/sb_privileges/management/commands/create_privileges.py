from json import loads
from django.core.management.base import BaseCommand
from django.conf import settings

from neomodel import CypherException

from sb_privileges.neo_models import (SBPrivilege, SBRestriction, SBAction)
from sb_requirements.neo_models import Requirement


class Command(BaseCommand):
    args = 'None.'
    help = 'Creates privilege, requirement, action and restrictions.'

    def create_privileges(self):
        with open('%s/sb_privileges/management/commands'
                  '/privilege_nodes.json' % settings.PROJECT_DIR,
                  'r') as data_file:
            data = loads(data_file.read())
            for privilege in data['privileges']:
                requirements = privilege.pop('requirements', [])
                actions = privilege.pop('actions', [])
                try:
                    privilege = SBPrivilege(**privilege).save()
                except CypherException:
                    pass
                for requirement in requirements:
                    try:
                        req = Requirement(**requirement).save()
                        privilege.requirements.connect(req)
                    except CypherException:
                        pass
                for action in actions:
                    try:
                        action = SBAction(**action).save()
                        privilege.actions.connect(action)
                    except CypherException:
                        pass
            for action in data['actions']: #for possible future use of single actions not connected with a privilege
                try:
                    action = SBAction(**action).save()
                except CypherException:
                    pass
            for restriction in data['restrictions']:
                try:
                    restriction = SBRestriction(**restriction).save()
                except CypherException as e:
                    pass


    def handle(self, *args, **options):
        self.create_privileges()
        print "Created all nodes"