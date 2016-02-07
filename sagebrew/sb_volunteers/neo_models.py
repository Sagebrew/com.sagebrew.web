from neomodel import (StringProperty, RelationshipTo)

from api.neo_models import SBObject


class Volunteer(SBObject):
    option = StringProperty(unique_index=True)
    # relationships
    volunteer_for = RelationshipTo('sb_missions.neo_models.Mission', 'FOR_THE')

