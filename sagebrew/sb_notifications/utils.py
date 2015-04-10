from logging import getLogger
from uuid import uuid1

from neomodel import DoesNotExist, CypherException

from .neo_models import NotificationBase
from sb_base.decorators import apply_defense

logger = getLogger('loggly_logs')


@apply_defense
def create_notification_util(sb_object, from_pleb, to_plebs,
                             notification_id=None):
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
    if from_pleb in to_plebs:
        to_plebs.remove(from_pleb)
    if notification_id is None:
        notification_id = str(uuid1())
    try:
        try:
            notification = NotificationBase.nodes.get(
                object_uuid=notification_id)
            if notification.sent is True:
                return True

        except (NotificationBase.DoesNotExist, DoesNotExist):
            try:
                notification = NotificationBase(
                    object_uuid=notification_id,
                    about=sb_object.sb_name,
                    about_id=sb_object.object_uuid,
                    url=sb_object.get_url(),
                    action=sb_object.action).save()
            except AttributeError:
                # Currently comments do not support notifications as there is
                # no easy way to get the object's url that the comment was
                # made on.
                logger.exception("Notification failure")
                return True

        notification.notification_from.connect(from_pleb)
        for pleb in to_plebs:
            notification.notification_to.connect(pleb)
            pleb.notifications.connect(notification)
        notification.sent = True
        notification.save()

        return True

    except CypherException as e:
        return e

