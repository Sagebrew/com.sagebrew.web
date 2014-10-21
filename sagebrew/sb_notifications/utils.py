import logging
from uuid import uuid1
from json import dumps

from neomodel import DoesNotExist, CypherException, UniqueProperty

from .neo_models import NotificationBase
from api.utils import determine_id
from sb_posts.neo_models import SBPost
from sb_comments.neo_models import SBComment
from plebs.neo_models import Pleb

logger = logging.getLogger('loggly_logs')

def create_notification_util(sb_object, object_type, from_pleb, to_plebs,
                             notification_id):
    '''
    This function will check to see if there is already a notification
    created about the combination of object, plebs, and action and will add
    another person to the from or to pleb if there is another. Also it
    will create the notification if one does not exist.

    :param sb_object:
    :param object_type:
    :param from_pleb:
    :param to_pleb:
    :return:
    '''

    if from_pleb in to_plebs:
        to_plebs.remove(from_pleb)

    try:
        try:
            notification = NotificationBase.nodes.get(
                notification_uuid=notification_id)
            if notification.sent:
                return {"detail": True}

        except (NotificationBase.DoesNotExist, DoesNotExist):
            notification = NotificationBase(notification_uuid=notification_id,
                                            notification_about=object_type).\
                save()

        notification.notification_from.connect(from_pleb)
        for pleb in to_plebs:
            notification.notification_to.connect(pleb)
            pleb.notifications.connect(notification)
        notification.sent=True
        notification.save()
        return {"detail": True}

    except CypherException:
        return {"detail": "retry"}
    except Exception:
        logger.exception(dumps({"function": create_notification_util.__name__,
                                "exception": "UnhandledException: "}))
        return {"detail": "retry"}

