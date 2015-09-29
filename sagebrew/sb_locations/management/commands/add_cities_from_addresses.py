from django.core.management.base import BaseCommand

from plebs.neo_models import Address
from sb_locations.neo_models import Location


class Command(BaseCommand):
    args = "None."

    def add_cities_from_addresses(self):
        wixom = Location.nodes.get(
            object_uuid="3ed3dfe8-5bc4-11e5-8dd9-0242ac110003")
        for location in wixom.encompassed_by.all():
            if location.name == "11":
                wixom.encompassed_by.disconnect(location)
                location.encompasses.disconnect(wixom)

        for address in Address.nodes.all():
            address.set_encompassing()

    def handle(self, *args, **options):
        self.add_cities_from_addresses()
