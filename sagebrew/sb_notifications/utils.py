import logging
from uuid import uuid1

from neomodel import DoesNotExist

from .neo_models import NotificationBase
from sb_posts.neo_models import SBPost
from sb_comments.neo_models import SBComment
from plebs.neo_models import Pleb

logger = logging.getLogger('loggly_logs')

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
