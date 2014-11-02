import logging
from celery import shared_task

from .utils import create_friend_request_util

logger = logging.getLogger("loggly_logs")

@shared_task()
def create_friend_request_task(data):
    try:
        res = create_friend_request_util(data)
        if isinstance(res, Exception):
            return create_friend_request_task.retry(exc=res, countdown=3,
                                                    max_retries=None)
        return res
    except Exception as e:
        logger.exception({"function": create_friend_request_task.__name__,
                          "exception": "UnhandledException"})
        raise create_friend_request_task.retry(exc=e, countdown=3,
                                               max_retries=None)