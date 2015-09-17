import os
from django.core.management.base import BaseCommand

from sb_campaigns.utils import release_single_donation


class Command(BaseCommand):
    args = 'None.'

    def release_single_donation_command(self):
        branch = os.environ.get("CIRCLE_BRANCH")
        if branch == 'master':
            release_single_donation("30cdd95c-5d46-11e5-93e3-0242ac110003")

    def handle(self, *args, **options):
        self.release_single_donation_command()
