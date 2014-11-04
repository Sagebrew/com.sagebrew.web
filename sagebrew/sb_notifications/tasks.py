import logging
from json import dumps
from celery import shared_task

from .utils import create_notification_util

logger = logging.getLogger('loggly_logs')


@shared_task()
def spawn_notifications(sb_object, from_pleb, to_plebs, uuid=None):
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
        response = create_notification_util(sb_object, from_pleb, to_plebs,
                                            uuid)
        if isinstance(response, Exception) is True:
            raise response
        return response

    except Exception as e:
        logger.exception(dumps({"function": spawn_notifications.__name__,
                                "exception": "Unhandled Exception"}))
        raise spawn_notifications.retry(exc=e, countdown=3, max_retries=None)

