from logging import getLogger
from json import loads

from django.core.management.base import BaseCommand
from django.conf import settings

from neomodel import CypherException, DoesNotExist

from govtrack.neo_models import GTPerson, GTRole
from sb_reps.neo_models import BaseOfficial

logger = getLogger('loggly_logs')

class Command(BaseCommand):
    args = 'None.'
    help = 'Creates placeholder representatives.'

    def create_placeholders(self):
        try:
            roles = GTRole.nodes.all()
        except (IOError, CypherException):
            return False
        for role in roles:
            if role.current:
                try:
                    person = role.person.all()[0]
                except IndexError:
                    continue
                #rep = BaseOfficial



    def handle(self, *args, **options):
        self.create_placeholders()
