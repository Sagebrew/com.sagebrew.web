import pytz
from uuid import uuid1

from datetime import datetime

from neomodel import (StructuredNode, StringProperty, DateTimeProperty,
                      RelationshipTo, BooleanProperty)


def get_current_time():
    return datetime.now(pytz.utc)


class NotificationBase(StructuredNode):
    object_uuid = StringProperty(default=uuid1, unique_index=True)
    seen = BooleanProperty(default=False)
    time_sent = DateTimeProperty(default=get_current_time)
    time_seen = DateTimeProperty(default=None)
    about = StringProperty()
    about_id = StringProperty()
    sent = BooleanProperty(default=False)
    url = StringProperty()
    action = StringProperty()

    # relationships
    notification_from = RelationshipTo('plebs.neo_models.Pleb',
                                       'NOTIFICATION_FROM')
    notification_to = RelationshipTo('plebs.neo_models.Pleb',
                                     'NOTIFICATION_TO')
