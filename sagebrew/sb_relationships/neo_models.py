import pytz
from datetime import datetime
from neomodel import (StructuredNode, StringProperty, DateTimeProperty,
                      RelationshipTo, StructuredRel,
                      BooleanProperty)


class FriendRelationship(StructuredRel):
    since = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    type = StringProperty(default="friends")
    currently_friends = BooleanProperty(default=True)
    time_unfriended = DateTimeProperty(default=None)
    who_unfriended = StringProperty()
    # who_unfriended = RelationshipTo("Pleb", "")



class FriendRequest(StructuredNode):
    friend_request_uuid = StringProperty(unique_index=True)
    seen = BooleanProperty(default=False)
    time_sent = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    time_seen = DateTimeProperty(default=None)
    response = StringProperty(default=None)


    # relationships
    request_from = RelationshipTo('plebs.neo_models.Pleb', 'REQUEST_FROM')
    request_to = RelationshipTo('plebs.neo_models.Pleb', 'REQUEST_TO')