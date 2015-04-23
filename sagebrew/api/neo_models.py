import pytz
from datetime import datetime
from uuid import uuid1

from neomodel import (StructuredNode, StringProperty, DateTimeProperty)


def get_current_time():
    return datetime.now(pytz.utc)


class SBObject(StructuredNode):
    __abstract_node__ = True

    object_uuid = StringProperty(default=uuid1, index=True)
    created = DateTimeProperty(default=get_current_time)
