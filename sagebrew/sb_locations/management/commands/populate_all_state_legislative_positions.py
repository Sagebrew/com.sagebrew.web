import us
import json
import urllib3

from django.core.management.base import BaseCommand

from neomodel import db

from sb_quests.neo_models import Position
from sb_locations.neo_models import Location


class Command(BaseCommand):
    args = "None."

    def populate_all_state_legislative_positions(self):
        base_url = 'http://openstates.org/api/v1/districts/%s/%s/'
        http = urllib3.PoolManager()
        for state in us.states.STATES:
            query = 'MATCH (l:Location {name:"%s", sector:"federal"}) ' \
                    'RETURN l' % state.name
            res, _ = db.cypher_query(query)
            state_node = Location.inflate(res.one)
            abbr = state.abbr.lower()
            lookup_url = base_url % (abbr, "upper")
            response = http.request('GET', lookup_url)
            json_response = json.loads(response.data)
            for district in json_response:
                location = Location(
                    name=district['name'], sector='state_upper').save()
                position = Position(
                    name="Senator for %s's %s District" %
                         (state_node.name, district['name']),
                    sector="state_upper").save()
                state_node.encompasses.connect(location)
                location.encompassed_by.connect(state_node)
                location.positions.connect(position)
                position.location.connect(location)

            lookup_url = base_url % (abbr, "lower")
            response = http.request('GET', lookup_url)
            json_response = json.loads(response.data)
            for district in json_response:
                location = Location(
                    name=district["name"], sector="state_lower").save()
                position = Position(
                    name="House Representative for %s's %s District" %
                         (state_node.name, district['name']),
                    sector="state_lower").save()
                state_node.encompasses.connect(location)
                location.encompassed_by.connect(state_node)
                location.positions.connect(position)
                position.location.connect(location)

        return True

    def handle(self, *args, **options):
        self.populate_all_state_legislative_positions()
