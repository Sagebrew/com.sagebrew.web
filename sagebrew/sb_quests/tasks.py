from celery import shared_task

from .utils import release_funds, release_single_donation


@shared_task()
def release_funds_task(goal_uuid):
    res = release_funds(goal_uuid)
    if isinstance(res, Exception):
        # 900second/15minute countdown to make sure that nobody gets billed
        # twice
        raise release_funds_task.retry(exc=res, countdown=900,
                                       max_retries=None)
    return res


@shared_task()
def release_single_donation_task(donation_uuid):
    res = release_single_donation(donation_uuid)
    if isinstance(res, Exception):
        # Short countdown here because the user should be receiving the email
        # not long after donating
        raise release_single_donation_task.retry(exc=res, countdown=10,
                                                 max_retries=None)
    return res
