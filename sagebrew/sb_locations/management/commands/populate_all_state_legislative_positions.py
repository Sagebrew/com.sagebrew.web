import us
import json
from django.core.management.base import BaseCommand

from neomodel import db

from sb_quests.neo_models import Position
from sb_locations.neo_models import Location


class Command(BaseCommand):
    args = "None."

    def populate_all_state_legislative_positions(self):
        for state in us.states.STATES:
            query = 'MATCH (l:Location {name:"%s", sector:"federal"}) ' \
                    'RETURN l' % state.name
            res, _ = db.cypher_query(query)
            state_node = Location.inflate(res.one)
            abbr = state.abbr.lower()
            with open('sb_locations/management/'
                      'commands/state_legislature/'
                      '%s/upper.json' % abbr) as data_file:
                for district in json.load(data_file):
                    query = 'MATCH (l:Location {object_uuid:"%s"}) WITH l ' \
                            'OPTIONAL MATCH (l)-[:ENCOMPASSES]->(l2:Location ' \
                            '{name:"%s", sector:"state_upper"}) WITH l, l2 ' \
                            'OPTIONAL MATCH (l2)-[:POSITIONS_AVAILABLE]->' \
                            '(p:Position {name:"State Senator", level:' \
                            '"state_upper"}) RETURN l2, p' % \
                            (state_node.object_uuid, district['name'])
                    res, _ = db.cypher_query(query)
                    try:
                        location = Location.inflate(res[0].l2)
                    except (IndexError, AttributeError):
                        location = Location(
                            name=district['name'], sector='state_upper').save()
                    try:
                        position = Position.inflate(res[0].p)
                    except (IndexError, AttributeError):
                        position = Position(
                            name="State Senator", level="state_upper").save()
                    if location not in state_node.encompasses:
                        state_node.encompasses.connect(location)
                    if state_node not in location.encompasses:
                        location.encompassed_by.connect(state_node)
                    if location not in position.location:
                        position.location.connect(location)
                    if not position.full_name:
                        full_name = Position.get_full_name(
                            position.object_uuid)
                        position.full_name = full_name['full_name']
                        position.save()

            with open('sb_locations/management/'
                      'commands/state_legislature/'
                      '%s/lower.json' % abbr) as data_file:
                for district in json.load(data_file):
                    query = 'MATCH (l:Location {object_uuid:"%s"}) WITH l ' \
                            'OPTIONAL MATCH (l)-[:ENCOMPASSES]->(l2:Location ' \
                            '{name:"%s", sector:"state_lower"}) WITH l, l2 ' \
                            'OPTIONAL MATCH (l2)-[:POSITIONS_AVAILABLE]->' \
                            '(p:Position {name:"State House Representative", ' \
                            'level:"state_lower"}) RETURN l2, p' % \
                            (state_node.object_uuid, district['name'])
                    res, _ = db.cypher_query(query)
                    try:
                        location = Location.inflate(res[0].l2)
                    except (IndexError, AttributeError):
                        location = Location(
                            name=district["name"], sector="state_lower").save()
                    try:
                        position = Position.inflate(res[0].p)
                    except (IndexError, AttributeError):
                        position = Position(
                            name="State House Representative",
                            level="state_lower").save()
                    if location not in state_node.encompasses:
                        state_node.encompasses.connect(location)
                    if state_node not in location.encompasses:
                        location.encompassed_by.connect(state_node)
                    if location not in position.location:
                        position.location.connect(location)
                    if not position.full_name:
                        full_name = Position.get_full_name(
                            position.object_uuid)
                        position.full_name = full_name['full_name']
                        position.save()

        return True

    def handle(self, *args, **options):
        self.populate_all_state_legislative_positions()
