from neomodel import DoesNotExist, CypherException

from plebs.neo_models import Pleb
from .neo_models import Badge


def manage_badges(username):
    earned = []
    try:
        badges = Badge.nodes.all()
    except CypherException as e:
        return e
    try:
        pleb = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException) as e:
        return e
    for badge in badges:
        if badge in pleb.badges.all():
            continue
        if badge.check_requirements(username):
            pleb.badges.connect(badge)
            earned.append(badge)
    return earned