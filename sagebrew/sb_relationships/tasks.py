from celery import shared_task

from .utils import create_friend_request_util


@shared_task()
def create_friend_request_task(data):
    res = create_friend_request_util(data)
    if isinstance(res, Exception):
        return create_friend_request_task.retry(exc=res, countdown=3,
                                                max_retries=None)
    return res
