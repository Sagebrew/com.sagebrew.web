from celery import shared_task

from .utils import create_friend_request_util


@shared_task()
def create_friend_request_task(data):
    if create_friend_request_util(data):
        return True
    else:
        return False