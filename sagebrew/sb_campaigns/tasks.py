from celery import shared_task

from .utils import release_funds


@shared_task()
def release_funds_task(goal_uuid):
    res = release_funds(goal_uuid)
    if isinstance(res, Exception):
        # 900second/15minute countdown to make sure that nobody gets billed
        # twice
        raise release_funds_task.retry(exc=res, countdown=900,
                                       max_retries=None)
    return res
