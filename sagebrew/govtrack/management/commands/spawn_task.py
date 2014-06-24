from django.core.management.base import BaseCommand
from django.conf import settings

from govtrack.tasks import (populate_gt_committee, populate_gt_person, populate_gt_role,
                            populate_gt_votes)

class Command(BaseCommand):
    args = 'None.'
    help = 'Test the conductor api endpoints.'
    #TODO set up functions to use the govtrack bulk data to get complete sets of data
    def handle(self, *args, **options):
        ROLE_URL='https://www.govtrack.us/api/v2/role?limit=600&offset=10000&current=True'
        populate_gt_role(ROLE_URL)
        print "Role and Person objects populated for current senators"

