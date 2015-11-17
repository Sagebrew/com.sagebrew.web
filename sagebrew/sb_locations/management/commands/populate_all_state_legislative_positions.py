import us
import requests

from django.core.management.base import BaseCommand

from neomodel import db

from sb_quests.neo_models import Position
from sb_locations.neo_models import Location


class Command(BaseCommand):
    args = "None."

    def populate_all_state_legislative_positions(self):
        base_url = 'http://openstates.org/api/v1/districts/%s/%s/'
        for state in us.states.STATES:
            query = 'MATCH (l:Location {name:"%s", sector:"federal"}) ' \
                    'RETURN l' % state.name
            res, _ = db.cypher_query(query)
            state_node = Location.inflate(res.one)
            abbr = state.abbr.lower()
            lookup_url = base_url % (abbr, "upper")
            response = requests.get(
                lookup_url,
                headers={"content-type": 'application/json; charset=utf8'})
            json_response = response.json()
            for district in json_response:
                location = Location(
                    name=district['name'], sector='state_upper').save()
                position = Position(
                    name="State Senator", level="state_upper").save()
                if location not in state_node.encompasses:
                    state_node.encompasses.connect(location)
                if state_node not in location.encompasses:
                    location.encompassed_by.connect(state_node)
                if position not in location.positions:
                    location.positions.connect(position)
                if location not in position.location:
                    position.location.connect(location)

            lookup_url = base_url % (abbr, "lower")
            response = requests.get(
                lookup_url,
                headers={"content-type": 'application/json; charset=utf8'})
            json_response = response.json()
            for district in json_response:
                location = Location(
                    name=district["name"], sector="state_lower").save()
                position = Position(
                    name="State House Representative",
                    level="state_lower").save()
                if location not in state_node.encompasses:
                    state_node.encompasses.connect(location)
                if state_node not in location.encompasses:
                    location.encompassed_by.connect(state_node)
                if position not in location.positions:
                    location.positions.connect(position)
                if location not in position.location:
                    position.location.connect(location)

        return True

    def handle(self, *args, **options):
        self.populate_all_state_legislative_positions()
