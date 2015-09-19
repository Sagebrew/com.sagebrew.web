from django.core.management.base import BaseCommand

from plebs.neo_models import Address
from sb_locations.neo_models import Location


class Command(BaseCommand):
    args = "None."

    def add_cities_from_addresses(self):
        for address in Address.nodes.all():
            location = Location(name=address.city).save()
            address.encompassed_by.connect(location)
            location.addresses.connect(address)

    def handle(self, *args, **options):
        self.add_cities_from_addresses()
