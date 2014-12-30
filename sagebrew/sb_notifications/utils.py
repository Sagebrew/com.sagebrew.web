from uuid import uuid1

from neomodel import DoesNotExist, CypherException

from sb_docstore.utils import add_object_to_table
from .neo_models import NotificationBase
from sb_base.decorators import apply_defense


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
                sb_id=notification_id)
            if notification.sent is True:
                return True

        except (NotificationBase.DoesNotExist, DoesNotExist):
            notification = NotificationBase(
                sb_id=notification_id,
                notification_about=sb_object.sb_name).save()

        notification.notification_from.connect(from_pleb)
        for pleb in to_plebs:
            notification.notification_to.connect(pleb)
            pleb.notifications.connect(notification)
            notification_data = {'email': pleb.email,
                                 'from_pleb': from_pleb.email,
                                 'notification_about': sb_object.sb_name,
                                 'notification_about_id': sb_object.sb_id,
                                 'notification_id': str(notification_id)}
            add_object_to_table('notifications', notification_data)
        notification.sent = True
        notification.save()

        return True

    except CypherException as e:
        return e

