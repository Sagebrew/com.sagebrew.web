from celery import shared_task

from .utils import (save_experience, save_bio,
                    save_goal, save_rep)


@shared_task()
def save_experience_task(rep_id, title, start_date, end_date, current,
                         company, location, exp_id, description=""):
    experience = save_experience(rep_id, title, start_date, end_date, current,
                                 company, location, exp_id, description)
    if isinstance(experience, Exception):
        raise save_experience_task.retry(exc=experience, countdown=3,
                                         max_retries=None)
    return True

@shared_task()
def save_bio_task(rep_id, bio):
    bio = save_bio(rep_id, bio)
    if isinstance(bio, Exception):
        raise save_bio_task.retry(exc=bio, countdown=3, max_retries=None)
    return True

@shared_task()
def save_goal_task(rep_id, vote_req, money_req, initial, description, goal_id):
    goal = save_goal(rep_id, vote_req, money_req, initial, description,
                     goal_id)
    if isinstance(goal, Exception):
        raise save_goal_task.retry(exc=goal, countdown=3, max_retries=None)
    return True

@shared_task()
def create_rep_task(pleb_username, rep_type, rep_id, recipient_id, gov_phone,
               customer_id=None):
    rep = save_rep(pleb_username, rep_type, rep_id, recipient_id, gov_phone,
                   customer_id)
    if isinstance(rep, Exception):
        raise create_rep_task.retry(exc=rep, countdown=3, max_retries=None)
    return True