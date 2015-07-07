from celery import shared_task

from sb_council.utils import update_masked, council_decision


@shared_task()
def update_masked_task(object_uuid):
    res = update_masked(object_uuid)
    if isinstance(res, Exception) is True:
        raise update_masked_task.retry(exc=res, countdown=3, max_retries=None)
    return res

@shared_task()
def council_decision_task():
    res = council_decision()
    if isinstance(res, Exception) is True:
        # the countdown here is set to a minute just to make sure that the db
        # has a chance to recover from the large amount of hits it will
        # receive during the task execution.
        raise council_decision_task.retry(exc=res, countdown=60,
                                          max_retries=None)
    return res