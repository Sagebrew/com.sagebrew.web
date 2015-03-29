import time
from django.core.management.base import BaseCommand
from django.conf import settings

from govtrack.tasks import populate_gt_role


class Command(BaseCommand):
    args = 'None.'
    help = 'Create all GT nodes associated with an api url from govtrack'

    def populate_gt_reps(self):
        res = populate_gt_role.apply_async(
            kwargs={"requesturl": "https://www.govtrack.us/api/v2/role?"
                                  "state=MI&current=true"})
        while not res.ready():
            time.sleep(1)
        print "Created GT Objects"

    def handle(self, *args, **options):
        self.populate_gt_reps()