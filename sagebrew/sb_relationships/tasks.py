from celery import shared_task

from .utils import create_friend_request_util


@shared_task()
def create_friend_request_task(from_username, to_username, object_uuid):
    res = create_friend_request_util(from_username, to_username, object_uuid)
    if isinstance(res, Exception):
        return create_friend_request_task.retry(exc=res, countdown=3,
                                                max_retries=None)
    return res
