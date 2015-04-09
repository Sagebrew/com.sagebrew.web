import pytz
from datetime import datetime

from neomodel import (StringProperty, StructuredRel, DateTimeProperty)

from sb_base.neo_models import SBVoteableContent


def get_current_time():
    return datetime.now(pytz.utc)


class FlagRelationship(StructuredRel):
    flag_time = DateTimeProperty(default=get_current_time)


class SBFlag(SBVoteableContent):
    reputation_loss = 10
    flag_type = StringProperty()
