import pytz

from datetime import datetime

from neomodel import (StringProperty, DateTimeProperty, RelationshipTo,
                      BooleanProperty)

from api.neo_models import SBObject


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


class NotificationCapable(SBObject):
    action_name = ''
    views = RelationshipTo('sb_stats.neo_models.SBViewCount', 'VIEWED')
