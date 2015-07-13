from celery import shared_task

from .utils import update_closed, check_closed_reputation_changes

from logging import getLogger
logger = getLogger('loggly_logs')


@shared_task()
def update_closed_task(object_uuid):
    res = update_closed(object_uuid)
    if isinstance(res, Exception) is True:
        raise update_closed_task.retry(exc=res, countdown=300,
                                       max_retries=None)
    return res


@shared_task()
def check_closed_reputation_changes_task():
    res = check_closed_reputation_changes()
    if isinstance(res, Exception) is True:
        # the countdown here is set to a minute just to make sure that the db
        # has a chance to recover from the large amount of hits it will
        # receive during the task execution.
        raise check_closed_reputation_changes_task.retry(exc=res, countdown=60,
                                                         max_retries=None)
    logger.critical('Scheduled reputation update task ran!')
    return res
