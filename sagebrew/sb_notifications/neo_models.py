import pytz

from datetime import datetime

from neomodel import (StructuredNode, StringProperty, DateTimeProperty,
                      RelationshipTo, BooleanProperty)


class NotificationBase(StructuredNode):
    object_uuid = StringProperty(unique_index=True)
    seen = BooleanProperty(default=False)
    time_sent = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    time_seen = DateTimeProperty(default=None)
    notification_about = StringProperty()
    notification_about_id = StringProperty()
    sent = BooleanProperty(default=False)

    # relationships

    notification_from = RelationshipTo('plebs.neo_models.Pleb',
                                       'NOTIFICATION_FROM')
    notification_to = RelationshipTo('plebs.neo_models.Pleb',
                                     'NOTIFICATION_TO')

class NotificationAction(NotificationBase):
    url = StringProperty()

    #relationships
