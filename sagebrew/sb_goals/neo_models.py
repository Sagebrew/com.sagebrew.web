from neomodel import (StringProperty, IntegerProperty,
                      BooleanProperty, RelationshipTo)

from api.neo_models import SBObject


class Goal(SBObject):
    initial = BooleanProperty(default=False)
    description = StringProperty()
    pledged_vote_requirement = IntegerProperty()
    monetary_requirement = IntegerProperty()

    # relationships
    updates = RelationshipTo('sb_goals.neo_models.Goal', "UPDATE_FOR")
    donations = RelationshipTo('sb_donations.neo_models.Donation', "RECEIVED")
    campaign = RelationshipTo('sb_campaigns.neo_models.Campaign', "SET_FOR")
    round = RelationshipTo('sb_')
