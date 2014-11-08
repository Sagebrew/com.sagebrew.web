import pytz
from uuid import uuid1
from datetime import datetime

from neomodel import (StructuredNode, BooleanProperty, StringProperty,
                      RelationshipTo, IntegerProperty, DateTimeProperty)


class SBVote(StructuredNode):
    vote_id = StringProperty(unique_index=True, default=lambda: str(uuid1()))
    vote_type = BooleanProperty() # True is up and False is down
    date_created = DateTimeProperty(default=lambda: datetime.now(pytz.utc))

    #relationships
    from_pleb = RelationshipTo('plebs.neo_models.Pleb', 'MADE_VOTE')
    vote_on = RelationshipTo('sb_posts.neo_models.SBContent', 'VOTE_ON')
