import pytz
from datetime import datetime

from neomodel import (StringProperty, StructuredRel, DateTimeProperty)

from sb_base.neo_models import SBVoteableContent


class FlagRelationship(StructuredRel):
    flag_time = DateTimeProperty(default=lambda: datetime.now(pytz.utc))


class SBFlag(SBVoteableContent):
    reputation_loss = 10
    flag_type = StringProperty()
