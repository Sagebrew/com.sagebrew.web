import pytz
from uuid import uuid1
from datetime import datetime

from neomodel import (StructuredNode, StringProperty, RelationshipTo,
                      BooleanProperty, StructuredRel, DateTimeProperty)

from sb_base.neo_models import SBVoteableContent

class FlagRelationship(StructuredRel):
    flag_time = DateTimeProperty(default=lambda: datetime.now(pytz.utc))

class SBFlag(SBVoteableContent):
    reputation_loss = 10
    flag_type = StringProperty()
