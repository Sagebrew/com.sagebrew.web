from celery import shared_task

from .utils import (save_bio, save_rep, determine_reps)


@shared_task()
def save_bio_task(rep_id, bio):
    bio = save_bio(rep_id, bio)
    if isinstance(bio, Exception):
        raise save_bio_task.retry(exc=bio, countdown=3, max_retries=None)
    return True


@shared_task()
def create_rep_task(pleb_username, rep_type, rep_id, recipient_id, gov_phone,
                    customer_id=None):
    rep = save_rep(pleb_username, rep_type, rep_id, recipient_id, gov_phone,
                   customer_id)
    if isinstance(rep, Exception):
        raise create_rep_task.retry(exc=rep, countdown=3, max_retries=None)
    return True


@shared_task()
def determine_rep_task(username):
    res = determine_reps(username)
    if isinstance(res, Exception):
        raise determine_rep_task.retry(exc=res, countdown=3, max_retries=None)
