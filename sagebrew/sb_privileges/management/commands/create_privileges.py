from json import loads
from django.core.management.base import BaseCommand
from django.conf import settings

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
                privilege = SBPrivilege(**privilege).save()
            for action in data['actions']:
                action = SBAction(**action).save()
            for restriction in data['restrictions']:
                restriction = SBRestriction(**restriction).save()
            

    def handle(self, *args, **options):
        self.create_privileges()
        print "Created all nodes"