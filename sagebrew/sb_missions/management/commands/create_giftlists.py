from django.core.management.base import BaseCommand

from sagebrew.sb_gifts.neo_models import Giftlist
from sagebrew.sb_missions.neo_models import Mission


class Command(BaseCommand):
    args = 'None.'

    def create_giftlists(self):
        for mission in Mission.nodes.all():
            if not mission.get_giftlist():
                giftlist = Giftlist().save()
                giftlist.mission.connect(mission)

    def handle(self, *args, **options):
        self.create_giftlists()
