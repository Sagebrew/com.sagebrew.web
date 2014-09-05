import pytz
from datetime import datetime
from django.conf import settings

from neomodel import (StructuredNode, StringProperty, DateTimeProperty,
                      RelationshipTo, StructuredRel,
                      BooleanProperty, IntegerProperty)


class FriendRelationship(StructuredRel):
    since = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    type = StringProperty(default="friends")
    currently_friends = BooleanProperty(default=True)
    time_unfriended = DateTimeProperty(default=None)
    who_unfriended = StringProperty()
    #who_unfriended = RelationshipTo("Pleb", "")

class UserWeightRelationship(StructuredRel):
    interaction = StringProperty(default='seen')
    page_view_count = IntegerProperty(default=0)
    weight = IntegerProperty(default=settings.USER_RELATIONSHIP_BASE['seen'])

class FriendRequest(StructuredNode):
    friend_request_uuid = StringProperty(unique_index=True)
    seen = BooleanProperty(default=False)
    time_sent = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    time_seen = DateTimeProperty(default=None)
    response = StringProperty(default=None)


    # relationships
    request_from = RelationshipTo('plebs.neo_models.Pleb', 'REQUEST_FROM')
    request_to = RelationshipTo('plebs.neo_models.Pleb', 'REQUEST_TO')