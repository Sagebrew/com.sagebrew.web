from neomodel import (StringProperty, IntegerProperty,
                      BooleanProperty, RelationshipTo, DateTimeProperty)

from api.neo_models import SBObject


class Goal(SBObject):
    initial = BooleanProperty(default=False)
    description = StringProperty()
    pledged_vote_requirement = IntegerProperty()
    monetary_requirement = IntegerProperty()

    # relationships
    updates = RelationshipTo('sb_updates.neo_models.Update', "UPDATE_FOR")
    donations = RelationshipTo('sb_donations.neo_models.Donation', "RECEIVED")
    campaign = RelationshipTo('sb_campaigns.neo_models.Campaign', "SET_FOR")
    round = RelationshipTo('sb_goals.neo_models.Rounds', "PART_OF")
    previous_goal = RelationshipTo('sb_goals.neo_models.Goal', "PREVIOUS")
    next_goal = RelationshipTo('sb_goals.neo_models.Goal', "NEXT")


class Round(SBObject):
    start_date = DateTimeProperty()
    end_data = DateTimeProperty()

    # relationships
    goals = RelationshipTo('sb_goals.neo_models.Goal', "STRIVING_FOR")
    previous_round = RelationshipTo('sb_goals.neo_models.Round', "PREVIOUS")
    next_round = RelationshipTo('sb_goals.neo_models.Round', "NEXT")
    campaign = RelationshipTo('sb_campaigns.neo_models.Campaign',
                              'ASSOCIATED_WITH')