from django.core.management.base import BaseCommand

from plebs.neo_models import Address
from sb_locations.neo_models import Location
from plebs.tasks import update_address_location


class Command(BaseCommand):
    def migrate_addresses(self):
        for address in Address.nodes.all():
            sector_list = []
            encompassed_by = address.get_all_encompassed_by()
            for encompassed_by_id in encompassed_by:
                loc = Location.nodes.get(object_uuid=encompassed_by_id)
                sector_list.append(loc.sector)
            print sector_list
            if "federal" not in sector_list:
                print 'here'
                update_address_location.apply_async(
                    kwargs={'object_uuid': address.object_uuid})
        return True

    def handle(self, *args, **options):
        self.migrate_addresses()
