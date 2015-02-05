from celery import shared_task

from .utils import manage_badges

@shared_task()
def check_badges(username):
    res = manage_badges(username)
    if isinstance(res, Exception):
        raise check_badges.retry(exc=res, countdown=3, max_retries=None)
    return res
