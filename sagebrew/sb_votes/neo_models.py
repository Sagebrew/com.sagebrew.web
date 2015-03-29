'''
import pytz
from uuid import uuid1
from datetime import datetime

from neomodel import (StructuredNode, BooleanProperty, StringProperty,
                      RelationshipTo, IntegerProperty, DateTimeProperty)

# Note to selves: We seem to keep discussing this but our plan is to add this
# in eventually, when we have time to setup useful analytics on it. We will
# want to be able to track how users vote's change from up to down on anything
# from changed versions of content or just over time. However to save room and
# time we have not added it in yet. When the time comes we'll grab a snapshot
# of everyone's vote relationships at the time and populate an initial vote
# node off of that. Then we will track the progression from there.

class SBVote(StructuredNode):
    vote_id = StringProperty(unique_index=True, default=lambda: str(uuid1()))
    vote_type = BooleanProperty() # True is up False is down None is undecided
    created = DateTimeProperty(default=lambda: datetime.now(pytz.utc))

    #relationships
    from_pleb = RelationshipTo('plebs.neo_models.Pleb', 'MADE_VOTE')
    vote_on = RelationshipTo('sb_base.neo_models.SBContent', 'VOTE_ON')

    def change_type(self, vote_type):
        self.vote_type = vote_type
        self.save()
        return self
'''