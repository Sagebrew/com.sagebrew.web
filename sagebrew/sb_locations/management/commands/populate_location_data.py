import os
import us
from json import loads, dumps

from neomodel import DoesNotExist, db

from django.core.management.base import BaseCommand

from sb_locations.neo_models import Location
from sb_campaigns.neo_models import Position


class Command(BaseCommand):
    args = 'None.'

    def populate_location_data(self):
        try:
            usa = Location.nodes.get(name='United States of America')
        except (DoesNotExist, Location.DoesNotExist):
            usa = Location(name="United States of America").save()
        if not usa.positions.all():
            pres = Position(name="President").save()
            usa.positions.connect(pres)
            pres.location.connect(usa)
        for root, dirs, files in \
                os.walk('sb_locations/management/commands/states/'):
            if not dirs:
                _, state = root.split("states/")
                state_name = us.states.lookup(state).name
                with open(root + "/" + files[0], 'r') as geo_data:
                    file_data = loads(geo_data.read())
                    try:
                        state = Location.nodes.get(name=state_name)
                    except (DoesNotExist, Location.DoesNotExist):
                        state = Location(name=state_name,
                                         geo_data=dumps(
                                             file_data['coordinates'])).save()
                    usa.encompasses.connect(state)
                    state.encompassed_by.connect(usa)
                    if not state.positions.all():
                        senator = Position(name='Senator').save()
                        senator.location.connect(state)
                        state.positions.connect(senator)
        for root, dirs, files in \
                os.walk('sb_locations/management/commands/districts/'):
            if files[0] != '.DS_Store':
                _, district_data = root.split('districts/')
                state, district = district_data.split('-')
                if not int(district):
                    district = 1
                state_node = Location.nodes.get(
                    name=us.states.lookup(state).name)
                with open(root + "/shape.geojson") as geo_data:
                    file_data = loads(geo_data.read())
                    query = 'MATCH (l:Location {name:"%s"})-[:ENCOMPASSES]->' \
                            '(d:Location {name:"%s"}) RETURN d' % \
                            (state_node.name, district)
                    res, _ = db.cypher_query(query)
                    if not res:
                        district = Location(name=int(district),
                                            geo_data=dumps(
                                            file_data['coordinates'])).save()
                        district.encompassed_by.connect(state_node)
                        district.encompassed_by.connect(usa)
                        usa.encompasses.connect(district)
                        state_node.encompasses.connect(district)
                        if not district.positions.all():
                            house_rep = Position(
                                name="House Representative").save()
                            house_rep.location.connect(district)
                            district.positions.connect(house_rep)
        return True

    def handle(self, *args, **options):
        self.populate_location_data()
