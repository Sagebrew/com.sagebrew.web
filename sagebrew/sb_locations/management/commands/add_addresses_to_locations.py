import us

from neomodel import db

from django.core.management.base import BaseCommand

from plebs.neo_models import Address
from sb_locations.neo_models import Location


class Command(BaseCommand):
    args = 'None.'

    def add_addresses_to_locations(self):
        for address in Address.nodes.all():
            if not address.encompassed_by.all():
                state = us.states.lookup(address.state)
                district = address.congressional_district
                query = 'MATCH (s:Location {name:"%s"})-[:ENCOMPASSES]->' \
                        '(d:Location {name:"%s"}) RETURN d' % \
                        (state, district)
                res, _ = db.cypher_query(query)
                district = Location.inflate(res[0][0])
                district.addresses.connect(address)
                address.encompassed_by.connect(district)


    def handle(self, *args, **options):
        self.add_addresses_to_locations()
