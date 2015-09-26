from django.core.management.base import BaseCommand

from plebs.neo_models import Address


class Command(BaseCommand):
    args = "None."

    def add_cities_from_addresses(self):
        for address in Address.nodes.all():
            address.set_encompassing()

    def handle(self, *args, **options):
        self.add_cities_from_addresses()
