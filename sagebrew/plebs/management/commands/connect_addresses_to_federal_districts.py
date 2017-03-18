from django.core.management.base import BaseCommand

from sagebrew.sb_locations.neo_models import Location
from sagebrew.sb_address.neo_models import Address
from sagebrew.sb_address.tasks import update_address_location


class Command(BaseCommand):

    def migrate_addresses(self):
        for address in Address.nodes.all():
            sector_list = []
            encompassed_by = address.get_all_encompassed_by()
            for encompassed_by_id in encompassed_by:
                loc = Location.nodes.get(object_uuid=encompassed_by_id)
                sector_list.append(loc.sector)
            if "federal" not in sector_list:
                update_address_location.apply_async(
                    kwargs={'object_uuid': address.object_uuid})
        return True

    def handle(self, *args, **options):
        self.migrate_addresses()
