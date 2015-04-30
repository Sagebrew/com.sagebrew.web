import pytz

from datetime import datetime

from django.conf import settings

from neomodel import (StringProperty, DateTimeProperty, RelationshipTo,
                      BooleanProperty, db)

from api.neo_models import SBObject
from sb_search.neo_models import Searchable


def get_current_time():
    return datetime.now(pytz.utc)


class Notification(SBObject):
    seen = BooleanProperty(default=False)
    time_sent = DateTimeProperty(default=get_current_time)
    time_seen = DateTimeProperty(default=None)
    about = StringProperty()
    about_id = StringProperty()
    sent = BooleanProperty(default=False)
    url = StringProperty()
    action_name = StringProperty()

    # relationships
    notification_from = RelationshipTo('plebs.neo_models.Pleb',
                                       'NOTIFICATION_FROM')
    notification_to = RelationshipTo('plebs.neo_models.Pleb',
                                     'NOTIFICATION_TO')


class NotificationCapable(Searchable):
    action_name = StringProperty(default="")
