from celery import shared_task

from .utils import create_friend_request_util
from sb_base.utils import defensive_exception


@shared_task()
def create_friend_request_task(data):
    try:
        res = create_friend_request_util(data)
        if isinstance(res, Exception):
            return create_friend_request_task.retry(exc=res, countdown=3,
                                                    max_retries=None)
        return res
    # TODO review this exception
    except Exception as e:
        raise defensive_exception(create_friend_request_task.__name__,
                                  e,
                                  create_friend_request_task.retry(exc=e,
                                                                   countdown=3,
                                                            max_retries=None))