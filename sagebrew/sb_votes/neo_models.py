import pytz
from uuid import uuid1
from datetime import datetime

from neomodel import (StructuredNode, BooleanProperty, StringProperty,
                      RelationshipTo, IntegerProperty, DateTimeProperty)


class SBVote(StructuredNode):
    vote_id = StringProperty(unique_index=True, default=lambda: str(uuid1()))
    vote_type = BooleanProperty() # True is up False is down None is undecided
    date_created = DateTimeProperty(default=lambda: datetime.now(pytz.utc))

    #relationships
    from_pleb = RelationshipTo('plebs.neo_models.Pleb', 'MADE_VOTE')
    vote_on = RelationshipTo('sb_base.neo_models.SBContent', 'VOTE_ON')

    def change_type(self, vote_type):
        self.vote_type = vote_type
        self.save()
        return self
