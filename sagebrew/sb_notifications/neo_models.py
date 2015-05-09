import pytz

from datetime import datetime

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
    sent = BooleanProperty(default=False)
    url = StringProperty()
    action_name = StringProperty()

    # relationships
    notification_from = RelationshipTo('plebs.neo_models.Pleb',
                                       'NOTIFICATION_FROM')
    notification_to = RelationshipTo('plebs.neo_models.Pleb',
                                     'NOTIFICATION_TO')

    @classmethod
    def unseen(cls, username):
        """
        Returns the amount of unseen notifications for a given user
        :param username:
        :return:
        """
        query = 'MATCH (a:Pleb {username: "%s"})-[:RECEIVED_A]->' \
            '(n:Notification) WHERE n.seen=false ' \
            'RETURN count(n)' % (username)
        res, col = db.cypher_query(query)
        return res[0][0]

    @classmethod
    def clear_unseen(cls, username):
        """
        Sets all the notifications for the given user to True so that there
        are no more unread notifications.

        Doesn't return anything because if the query fails a Cypher Exception
        is thrown and a 500 error will propagate out.
        :param username:
        :return:
        """
        query = 'MATCH (a:Pleb {username: "%s"})-[:RECEIVED_A]->' \
                '(n:Notification)' \
                ' SET n.seen = True' % (username)
        db.cypher_query(query)


class NotificationCapable(Searchable):
    action_name = StringProperty(default="")
