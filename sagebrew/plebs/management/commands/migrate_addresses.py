from localflavor.us.us_states import US_STATES

from django.core.management.base import BaseCommand

from sagebrew.sb_address.neo_models import Address


class Command(BaseCommand):

    def migrate_addresses(self):
        for address in Address.nodes.all():
            try:
                state = dict(US_STATES)[address.state]
            except KeyError:
                state = address.state
            address.state = state
            address.save()
        return True

    def handle(self, *args, **options):
        self.migrate_addresses()
