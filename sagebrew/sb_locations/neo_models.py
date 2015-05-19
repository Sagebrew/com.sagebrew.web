from neomodel import (StringProperty, IntegerProperty, RelationshipTo)

from api.neo_models import SBObject


class Country(SBObject):
    name = StringProperty()

    locations = RelationshipTo('sb_locations.neo_models.Location',
                               'ENCOMPASSES_LOCATION')
    states = RelationshipTo('sb_locations.neo_models.State',
                            'ENCOMPASSES_STATE')
    districts = RelationshipTo('sb_locations.neo_models.District',
                               'ENCOMPASSES_DISTRICT')


class Location(SBObject):
    geo_data = StringProperty()

    states = RelationshipTo('sb_locations.neo_models.State',
                            'ENCOMPASSES_STATE')


class State(SBObject):
    name = StringProperty()

    districts = RelationshipTo('sb_locations.neo_models.District',
                               'ENCOMPASSES_DISTRICT')


class District(SBObject):
    number = IntegerProperty()

    state = RelationshipTo('sb_locations.neo_models.State', 'ENCOMPASSED_BY')
    addresses = RelationshipTo('plebs.neo_models.Address',
                               'ENCOMPASSES_ADDRESS')
    positions_available = RelationshipTo('sb_campaigns.neo_models.Position',
                                         'HAS_POSITION')
