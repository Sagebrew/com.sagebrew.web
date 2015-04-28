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


class NotificationCapable(SBObject, Searchable):
    action_name = ''
    views = RelationshipTo('sb_stats.neo_models.Impression', 'VIEWED')

    def get_labels(self):
        query = 'START n=node(%d) RETURN DISTINCT labels(n)' % (self._id)
        res, col = db.cypher_query(query)
        return res[0][0]

    def get_child_label(self):
        """
        With the current setup the actual piece of content is the last
        label.

        This goes on the assumption that Neo4J returns labels in order of
        assignment. Since neomodel assigns these in order of inheritance
        the top most parent being first and the bottom child being last
        we assume that our actual real commentable object is last.

        This can be accomplished by ensuring that the content is the
        bottom most child in the hierarchy. Currently this is only used for
        determining what content a comment is actually associated with for
        url linking. The commented out logic below can be substituted if with
        a few additional items if this begins to not work

            def get_child_labels(self):
                parents = inspect.getmro(self.__class__)
                # Creates a generator that enables us to access all the
                # names of the parent classes
                parent_array = (o.__name__ for o in parents)
                child_array = list(set(self.get_labels()) - set(parent_array))
                return child_array

            def get_child_label(self):
                labels = self.get_labels()
                # If you want to comment on something the class name must be
                # listed here
                content = ['Post', 'Question', 'Solution']
                try:
                    set(labels).intersection(content).pop()
                except KeyError:
                    return ""

        :return:
        """
        return list(set(self.get_labels()) - set(settings.REMOVE_CLASSES))[0]
