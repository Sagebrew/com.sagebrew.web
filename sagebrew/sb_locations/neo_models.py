from neomodel import (StringProperty, IntegerProperty, RelationshipTo)

from api.neo_models import SBObject


class Location(SBObject):
    name = StringProperty()
    geo_data = StringProperty(default=None)

    encompasses = RelationshipTo('sb_locations.neo_models.Location',
                                 'ENCOMPASSES')
    encompassed_by = RelationshipTo('sb_locations.neo_models.Location',
                                    'ENCOMPASSED_BY')
    positions = RelationshipTo('sb_campaigns.neo_models.Position',
                               'POSITIONS_AVAILABLE')
