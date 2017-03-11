from django.core.management.base import BaseCommand

from neomodel import DoesNotExist

from sagebrew.sb_address.neo_models import Address
from sagebrew.sb_locations.neo_models import Location


class Command(BaseCommand):
    args = "None."

    def add_cities_from_addresses(self):
        try:
            wixom = Location.nodes.get(
                object_uuid="3ed3dfe8-5bc4-11e5-8dd9-0242ac110003")
            for location in wixom.encompassed_by.all():
                if location.name == "11":
                    wixom.encompassed_by.disconnect(location)
                    location.encompasses.disconnect(wixom)
        except (DoesNotExist, Location.DoesNotExist):
            pass
        for address in Address.nodes.all():
            address.set_encompassing()

    def handle(self, *args, **options):
        self.add_cities_from_addresses()
