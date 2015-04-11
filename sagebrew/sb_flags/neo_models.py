import pytz
from datetime import datetime

from neomodel import (StringProperty, StructuredRel, DateTimeProperty)

from sb_base.neo_models import VotableContent


def get_current_time():
    return datetime.now(pytz.utc)


class FlagRelationship(StructuredRel):
    flag_time = DateTimeProperty(default=get_current_time)


class Flag(VotableContent):
    reputation_loss = 10
    flag_type = StringProperty()
