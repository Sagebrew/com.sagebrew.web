from celery import shared_task

from .utils import check_goal_completion_util


@shared_task()
def check_goal_completion_task(round_uuid=None):
    res = check_goal_completion_util(round_uuid)
    if isinstance(res, Exception):
        raise check_goal_completion_task.retry(exc=res, countdown=3,
                                               max_retries=None)
    return res
