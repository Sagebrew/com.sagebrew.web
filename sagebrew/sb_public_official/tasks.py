from celery import shared_task

from .utils import determine_reps


@shared_task()
def determine_rep_task(username):
    res = determine_reps(username)
    if isinstance(res, Exception):
        raise determine_rep_task.retry(exc=res, countdown=3, max_retries=None)
