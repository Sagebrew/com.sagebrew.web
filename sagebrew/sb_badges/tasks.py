from celery import shared_task
from neomodel import DoesNotExist, CypherException

from api.utils import post_to_api
from plebs.neo_models import Pleb
from .neo_models import BadgeBase

@shared_task()
def check_badges(username):
    earned = []
    try:
        badges = BadgeBase.nodes.all()
    except CypherException as e:
        raise check_badges.retry(exc=e, countdown=3, max_retries=None)
    try:
        pleb = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException) as e:
        raise check_badges.retry(exc=e, countdown=3, max_retries=None)
    for badge in badges:
        if badge in pleb.badges.all():
            continue
        if badge.check_requirements(username):
            pleb.badges.connect(badge)
            earned.append(badge)
    return earned


