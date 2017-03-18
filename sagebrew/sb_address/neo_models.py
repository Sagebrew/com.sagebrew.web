import us

from neomodel import (StringProperty, IntegerProperty,
                      RelationshipTo, BooleanProperty, FloatProperty,
                      DoesNotExist, MultipleNodesReturned, db)

from sagebrew.api.utils import flatten_lists, spawn_task
from sagebrew.api.neo_models import SBObject
from sagebrew.sb_locations.neo_models import Location


class Address(SBObject):
    street = StringProperty()
    street_additional = StringProperty()
    city = StringProperty()
    state = StringProperty(index=True)
    postal_code = StringProperty(index=True)
    country = StringProperty()
    latitude = FloatProperty()
    longitude = FloatProperty()
    county = StringProperty()
    congressional_district = IntegerProperty()
    validated = BooleanProperty(default=False)

    # Relationships
    encompassed_by = RelationshipTo('sagebrew.sb_locations.neo_models.Location',
                                    'ENCOMPASSED_BY')

    def get_all_encompassed_by(self):
        query = 'MATCH (a:Address {object_uuid:"%s"})-[:ENCOMPASSED_BY]->' \
                '(l:Location) WITH l OPTIONAL MATCH (l)-' \
                '[:ENCOMPASSED_BY*1..3]->(l2:Location) RETURN ' \
                'distinct l.object_uuid, collect(distinct(l2.object_uuid))'\
                % self.object_uuid
        res, _ = db.cypher_query(query)
        return flatten_lists(res)  # flatten

    def set_encompassing(self):
        from .tasks import connect_to_state_districts
        try:
            encompassed_by = Location.nodes.get(name=self.city)
            if Location.get_single_encompassed_by(
                    encompassed_by.object_uuid) != \
                    us.states.lookup(self.state).name:
                # if a location node exists with an incorrect encompassing
                # state
                raise DoesNotExist("This Location does not exist")
        except (Location.DoesNotExist, DoesNotExist):
            encompassed_by = Location(name=self.city, sector="local").save()
            try:
                city_encompassed = Location.nodes.get(
                    name=us.states.lookup(self.state).name)
            except (Location.DoesNotExist, DoesNotExist):
                city_encompassed = Location(
                    name=us.states.lookup(self.state).name,
                    sector="federal").save()
            if city_encompassed not in encompassed_by.encompassed_by:
                encompassed_by.encompassed_by.connect(city_encompassed)
            if encompassed_by not in city_encompassed.encompasses:
                city_encompassed.encompasses.connect(encompassed_by)
        except (MultipleNodesReturned, Exception):
            query = 'MATCH (l1:Location {name:"%s"})-[:ENCOMPASSED_BY]->' \
                    '(l2:Location {name:"%s"}) RETURN l1' % \
                    (self.city, self.state)
            res, _ = db.cypher_query(query)
            res = res[0][0] if res else None
            if res is not None:
                encompassed_by = Location.inflate(res)
            else:
                encompassed_by = None
        if encompassed_by is not None:
            if encompassed_by not in self.encompassed_by:
                self.encompassed_by.connect(encompassed_by)
        # get or create the state level districts and attach them to the
        # address
        spawn_task(task_func=connect_to_state_districts,
                   task_param={'object_uuid': self.object_uuid})
        return self
