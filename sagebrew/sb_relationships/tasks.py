import logging
from celery import shared_task

from .utils import create_friend_request_util

logger = logging.getLogger("loggly_logs")

@shared_task()
def create_friend_request_task(data):
    try:
        res = create_friend_request_util(data)
        if res:
            return True
        elif res is None:
            return False
        else:
            raise Exception
    except Exception:
        logger.exception({"function": create_friend_request_task.__name__,
                          "exception": "UnhandledException:"})
        raise create_friend_request_task.retry(exc=Exception, countdown=3,
                                               max_retries=None)