import pytz

from datetime import datetime

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, ZeroOrOne)

class NotificationBase(StructuredNode):
    notification_uuid = StringProperty(unique_index=True)
    seen = BooleanProperty(default=False)
    time_sent = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    time_seen = DateTimeProperty(default=None)
    notification_about = StringProperty()
    notification_about_id = StringProperty()

    #relationships
    notification_from = RelationshipTo('plebs.neo_models.Pleb', 'NOTIFICATION_FROM')
    notification_to = RelationshipTo('plebs.neo_models.Pleb', 'NOTIFICATION_TO')

class FriendRequest(StructuredNode):
    friend_request_uuid = StringProperty(unique_index=True)
    seen = BooleanProperty(default=False)
    time_sent = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    time_seen = DateTimeProperty(default=None)
    response = StringProperty(default=None)


    #relationships
    request_from = RelationshipTo('plebs.neo_models.Pleb', 'REQUEST_FROM')
    request_to = RelationshipTo('plebs.neo_models.Pleb', 'REQUEST_TO')

