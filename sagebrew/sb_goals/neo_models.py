from neomodel import (StringProperty, IntegerProperty,
                      BooleanProperty, RelationshipTo, DateTimeProperty)

from api.neo_models import SBObject


class Goal(SBObject):
    """
    Goals are milestones set by campaigning individuals in an attempt to raise
    funds. Goals must have a monetary requirement and can have a
    pledged vote requirement. These are used to manage when donations will
    actually be billed against the user and given to the representative.
    Each goal should set a tangible achievement that can be obtained based on
    the requirements set. Each goal must also have an update associated with it
    after it has been reached. This way users can have some transparency as to
    how their donations are actually being used.
    Goals are organized into rounds in an attempt to make the assignment process
    more agile and reduce the strain on users of having to define all their
    goals up front.
    """
    # Programmaticly set based on the ordering of the goals in a round.
    # If a goal has no goals set for `previous_goal` this should be true.
    # May be able to replace this with a method or fully implement it in the
    # interface.
    initial = BooleanProperty(default=False)
    # This is what will be shown above each goal in the Action area. Titles
    # should describe what the goal is for in a couple words, around 40 chars.
    # Required
    title = StringProperty()
    # Summary is used to provide a summary of the description and should
    # lay out what the goal is attempting to accomplish in 300 or so characters.
    # This is may be shown in the Action area and can potentially be utilized
    # when a user clicks on a goal and is about to donate to it.
    # Required
    summary = StringProperty()
    # Description is the longer explanation of what the goal entails and why
    # it's being done. This may not be shown initially and can be optional.
    # We can provide this as the markdown area where a campaigner can go into
    # great detail regarding a given goal.
    # Optional
    description = StringProperty()
    pledged_vote_requirement = IntegerProperty(default=0)
    monetary_requirement = IntegerProperty(default=0)

    # relationships
    updates = RelationshipTo('sb_updates.neo_models.Update', "UPDATE_FOR")
    donations = RelationshipTo('sb_donations.neo_models.Donation', "RECEIVED")
    round = RelationshipTo('sb_goals.neo_models.Round', "PART_OF")
    previous_goal = RelationshipTo('sb_goals.neo_models.Goal', "PREVIOUS")
    next_goal = RelationshipTo('sb_goals.neo_models.Goal', "NEXT")
    campaign = RelationshipTo('sb_campaigns.neo_models.Campaign', 'SET_FOR')

    # TODO should we ever bind a goal to a single user? Or should it always
    # be bound to a campaign and project which are then bound to x amount of
    # users? May make queries easier but I think by not binding them tightly
    # we improve the distinction between a private profile and their active
    # public identity.


class Round(SBObject):
    """
    A round is a grouping of goals. The objective of a round is to provide
    more of an agile development feel to the goal assignment process. A round
    is much like a sprint only over a much longer duration. But within it
    the user defines which goals they'd like to accomplish and how much they'll
    need to raise to accomplish each. Then they can try and close out that
    round by achieving each of the goals, providing updates, and then start
    a new round.

    NOTE: Please be aware that you should not use `round` when instantiating
    this object. `round` is a keyword in Python relating to rounding. Please
    use something else to store the instance in.
    """
    # Start date should not be confused with `created` created is when the user
    # first defines the round, while start date is the day it goes public.
    # This gives us some flexibility with enabling users to set a time in the
    # future they would like the round to go active.
    start_date = DateTimeProperty()
    # Completed is a programmaticly set value that should be set when
    # the campaigner closes out a round by completing all the associated
    # goals.
    completed = DateTimeProperty()
    current = BooleanProperty(default=False)

    # relationships
    goals = RelationshipTo('sb_goals.neo_models.Goal', "STRIVING_FOR")
    previous_round = RelationshipTo('sb_goals.neo_models.Round', "PREVIOUS")
    next_round = RelationshipTo('sb_goals.neo_models.Round', "NEXT")
    campaign = RelationshipTo('sb_campaigns.neo_models.Campaign',
                              'ASSOCIATED_WITH')
