from localflavor.us.us_states import US_STATES

from django.core.management.base import BaseCommand

from sb_public_official.neo_models import PublicOfficial


class Command(BaseCommand):

    def migrate_states(self):
        for official in PublicOfficial.nodes.all():
            try:
                state = dict(US_STATES)[official.state]
            except KeyError:
                state = official.state
            official.state = state
            official.save()
        return True

    def handle(self, *args, **options):
        self.migrate_states()
