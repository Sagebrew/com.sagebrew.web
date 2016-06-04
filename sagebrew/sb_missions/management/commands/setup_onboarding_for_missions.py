from django.core.management.base import BaseCommand
from django.core.cache import cache


from sb_missions.neo_models import Mission
from sb_missions.utils import setup_onboarding


class Command(BaseCommand):
    args = 'None.'

    def setup_onboarding_retroactive(self):
        for mission in Mission.nodes.all():
            quest = Mission.get_quest(mission.object_uuid)
            setup_onboarding(quest, mission)

    def handle(self, *args, **options):
        self.setup_onboarding_retroactive()
