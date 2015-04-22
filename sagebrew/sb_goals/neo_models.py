from neomodel import (StringProperty, IntegerProperty,
                      BooleanProperty)

from api.neo_models import SBObject


class Goal(SBObject):
    initial = BooleanProperty(default=False)
    description = StringProperty()
    pledged_vote_requirement = IntegerProperty()
    monetary_requirement = IntegerProperty()
