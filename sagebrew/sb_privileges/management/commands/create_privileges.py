from json import loads
from django.core.management.base import BaseCommand
from django.conf import settings

from sb_privileges.neo_models import (SBPrivilege, SBRestriction, SBAction)
from sb_requirements.neo_models import Requirement


class Command(BaseCommand):
    args = 'None.'
    help = 'Creates privilege, requirement, action and restrictions.'

    def create_privileges(self):
        pass

    def handle(self, *args, **options):
        self.create_privileges()
        print "Created all nodes"