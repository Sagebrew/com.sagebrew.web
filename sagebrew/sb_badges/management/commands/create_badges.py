from json import loads
from django.core.management.base import BaseCommand
from django.conf import settings

from neomodel import CypherException

from sb_badges.neo_models import BadgeBase
from sb_requirements.neo_models import Requirement

class Command(BaseCommand):
    args = 'None.'
    help = 'Creates default badge nodes'

    def create_badges(self):
        with open('%s/sb_badges/management/commands'
                  '/badge_nodes.json' % settings.PROJECT_DIR,
                  'r') as data_file:
            data = loads(data_file.read())
            for badge in data:
                requirements = badge.pop('requirements', [])
                badge = BadgeBase(**badge).save()
                for requirement in requirements:
                    try:
                        req = Requirement(**requirement).save()
                        badge.requirements.connect(req)
                    except CypherException:
                        continue
                    print req.get_dict()
                print badge.get_dict()


    def handle(self, *args, **options):
        self.create_badges()
        print "Created all nodes"