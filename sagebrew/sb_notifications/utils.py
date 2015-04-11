from logging import getLogger

from neomodel import DoesNotExist, CypherException

from .neo_models import NotificationBase, NotificationCapable
from sb_base.decorators import apply_defense

logger = getLogger('loggly_logs')


@apply_defense
def create_notification_util(sb_object, from_pleb, to_plebs, notification_id,
                             url):
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
            notification = NotificationBase.nodes.get(
                object_uuid=notification_id)
            if notification.sent is True:
                return True

        except (NotificationBase.DoesNotExist, DoesNotExist):
            notification = NotificationBase(
                object_uuid=notification_id,
                about=sb_object.__class__.__name__.lower(),
                about_id=sb_object.object_uuid,
                url=url,
                action_name=sb_object.action_name).save()

        notification.notification_from.connect(from_pleb)
        for pleb in to_plebs:
            notification.notification_to.connect(pleb)
            pleb.notifications.connect(notification)
        notification.sent = True
        notification.save()

        return True

    except CypherException as e:
        return e

