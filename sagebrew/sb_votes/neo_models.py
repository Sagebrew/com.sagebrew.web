from neomodel import (BooleanProperty, IntegerProperty, RelationshipTo)

from sagebrew.api.neo_models import SBObject

# Note to selves: We seem to keep discussing this but our plan is to add this
# in eventually, when we have time to setup useful analytics on it. We will
# want to be able to track how users vote's change from up to down on anything
# from changed versions of content or just over time. However to save room and
# time we have not added it in yet. When the time comes we'll grab a snapshot
# of everyone's vote relationships at the time and populate an initial vote
# node off of that. Then we will track the progression from there.

# We're currently not using this still aside from a reference for the
# serializer


class Vote(SBObject):
    # 1 is Upvote (True) 0 is Downvote (False)
    # We aren't including None as a valid state as that would be a new action
    # taken by the user and a new Vote being cast. If they change we'd want to
    # update either a Relationship or spawn a new node with a new time. That
    # way we can track progression of votes based on changes to the content.
    vote_type = BooleanProperty()

    # optimizations
    reputation_change = IntegerProperty(default=0)
    # reputation_change allows us to easily calculate the amount of rep you
    # have gained or lost from an object over time

    owned_by = RelationshipTo('sagebrew.plebs.neo_models.Pleb', 'MADE_VOTE')
    vote_on = RelationshipTo(
        'sagebrew.sb_base.neo_models.VotableContent', 'VOTE_ON')
    next_vote = RelationshipTo(
        'sagebrew.sb_votes.neo_models.Vote', 'NEXT_VOTE')
