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

def create_notification_util(sb_object, object_type, from_pleb, to_pleb,
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

    if type(to_pleb) != list:
        if from_pleb == to_pleb:
            return {"detail": True}
    else:
        if from_pleb in to_pleb:
            to_pleb.remove(from_pleb)

    object_id = determine_id(sb_object, object_type)
    if not object_id:
        return {"detail": False}
    try:
        try:
            notification = NotificationBase.nodes.get(
                notification_uuid=notification_id)
            if notification.sent:
                return {"detail": True}

        except (NotificationBase.DoesNotExist, DoesNotExist):
            notification = NotificationBase(notification_uuid=notification_id,
                                            notification_about=object_type,
                                            notification_about_id=object_id).\
                save()

        notification.notification_from.connect(from_pleb)
        if type(to_pleb) == list:
            for pleb in to_pleb:
                notification.notification_to.connect(pleb)
                pleb.notifications.connect(notification)
        else:
            notification.notification_to.connect(to_pleb)
            to_pleb.notifications.connect(notification)
        notification.sent=True
        notification.save()
        return {"detail": True}

    except CypherException:
        return {"detail": "retry"}
    except Exception:
        logger.exception(dumps({"function": create_notification_util.__name__,
                                "exception": "UnhandledException: "}))
        return {"detail": "retry"}

def create_notification_post_util(post_uuid=str(uuid1()),
                                  from_pleb="", to_pleb=""):
    '''
    This function creates a notification about a post and creates the
    relationships

    :param post_uuid:
    :param from_pleb:
    :param to_pleb:
    :return:
            If the notification is successfully created returns True

            If the notification is not created returns False
    '''
    # TODO Review with Tyler. Does this check if a notification has already been
    # connected and if it has not create another?
    if from_pleb == to_pleb:
        return True
    try:
        try:
            from_citizen = Pleb.nodes.get(email=from_pleb)
            to_citizen = Pleb.nodes.get(email=to_pleb)
        except Pleb.DoesNotExist:
            return None
        except DoesNotExist:
            return None

        try:
            post = SBPost.nodes.get(post_id=post_uuid)
        except SBPost.DoesNotExist:
            return False
        except DoesNotExist:
            return False
        data = {'notification_uuid': str(uuid1()),
                'notification_about_id': post_uuid,
                'notification_about': 'post'}
        notification = NotificationBase(**data)
        notification.save()
        notification.notification_from.connect(from_citizen)
        notification.notification_to.connect(to_citizen)
        notification.save()
        to_citizen.notifications.connect(notification)
        to_citizen.save()
        return True
    except Exception:
        logger.exception({"function": create_notification_post_util.__name__,
                          "exception": "UnhandledException: "})
        return False

def create_notification_comment_util(from_pleb="", to_pleb="",
                                     comment_uuid=str(uuid1()),
                                     comment_on="",
                                     comment_on_id=str(uuid1())):
    try:
        if from_pleb == to_pleb:
            return True
        try:
            from_citizen = Pleb.nodes.get(email=from_pleb)
            to_citizen = Pleb.nodes.get(email=to_pleb)
        except Pleb.DoesNotExist:
            return None
        except DoesNotExist:
            return None

        try:
            comment = SBComment.nodes.get(comment_id = comment_uuid)
        except SBComment.DoesNotExist:
            return False
        except DoesNotExist:
            return False

        data = {'notification_uuid': str(uuid1()),
                'notification_about_id': comment_uuid,
                'notification_about': 'comment'}
        notification = NotificationBase(**data)
        notification.save()
        notification.notification_from.connect(from_citizen)
        notification.notification_to.connect(to_citizen)
        notification.save()
        to_citizen.notifications.connect(notification)
        to_citizen.save()
        return True
    except Exception:
        logger.exception({"function": create_notification_comment_util.__name__,
                          'exception': "UnhandledException: "})
        return False
