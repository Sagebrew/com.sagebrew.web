from logging import getLogger

from django.core.cache import cache

from neomodel import DoesNotExist, CypherException

from .neo_models import Notification, NotificationCapable
from sb_base.decorators import apply_defense

logger = getLogger('loggly_logs')


@apply_defense
def create_notification_util(sb_object, from_pleb, to_plebs, notification_id,
                             url, action_name, public=False):
    """
    This function will check to see if there is already a notification
    created about the combination of object, plebs, and action and will add
    another person to the from or to pleb if there is another. Also it
    will create the notification if one does not exist.

    :param sb_object:
    :param from_pleb:
    :param to_plebs:
    :param notification_id:
    :return:
    """
    try:
        sb_object = NotificationCapable.nodes.get(object_uuid=sb_object)
    except (CypherException, IOError) as e:
        return e

    try:
        try:
            notification = Notification.nodes.get(
                object_uuid=notification_id)
            if notification.sent is True:
                return True
        except (Notification.DoesNotExist, DoesNotExist):
            notification = Notification(
                object_uuid=notification_id,
                about=sb_object.__class__.__name__.lower(),
                url=url, public_notification=public,
                action_name=action_name).save()
        notification.notification_from.connect(from_pleb)
        for pleb in to_plebs:
            notification.notification_to.connect(pleb)
            # Set notifications to none here so that the next time the user
            # queries their page it refreshes. If we set this to the
            # notification list there is a chance for a race condition and the
            # user does not see all of their notifications.
            pleb.notifications.connect(notification)
            cache.delete("%s_notifications" % pleb.username)
        notification.sent = True
        notification.save()

        return True

    except (CypherException, IOError) as e:
        return e
