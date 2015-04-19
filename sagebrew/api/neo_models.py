import pytz
from datetime import datetime
from uuid import uuid1

from neomodel import (StructuredNode, StringProperty,
                      DateTimeProperty, BooleanProperty)


def get_current_time():
    return datetime.now(pytz.utc)


class SBObject(StructuredNode):
    object_uuid = StringProperty(default=uuid1, unique_index=True)
    created = DateTimeProperty(default=get_current_time)
    search_id = StringProperty()
    populated_es_index = BooleanProperty(default=False)
