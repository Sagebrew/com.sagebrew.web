import logging
from uuid import uuid1
from json import dumps
from celery import shared_task

from .utils import create_notification_util

logger = logging.getLogger('loggly_logs')


@shared_task()
def spawn_notifications(sb_object, object_type, from_pleb, to_plebs):
    '''
    This function will take an object(post,comment,answer,etc.), the type of
    the object, from_pleb and a to_pleb. To pleb can be a list of people or
    just a singular pleb and will create a notification about the object

    :param sb_object:
    :param object_type:
    :param from_pleb:
    :param to_pleb:
    :return:
    '''
    try:
        uuid = str(uuid1())
        res = create_notification_util(sb_object, object_type, from_pleb,
                                       to_plebs, uuid)
        if res['detail'] == 'retry':
            raise TypeError
        elif res['detail'] == True:
            return True

    except TypeError:
        raise spawn_notifications.retry(exc=TypeError, countdown=3,
                                        max_retries=None)
    except Exception:
        logger.exception(dumps({"function": spawn_notifications.__name__,
                                "exception": "UnhandledException: "}))
        raise spawn_notifications.retry(exc=Exception, countdown=3,
                                        max_retries=None)

