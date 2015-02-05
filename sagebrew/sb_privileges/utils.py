import pytz
from celery import shared_task
from datetime import datetime
from neomodel import (DoesNotExist, CypherException)

from plebs.neo_models import Pleb
from .neo_models import SBPrivilege

def manage_privilege_relation(username):
    try:
        pleb = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException) as e:
        return e
    try:
        privileges = SBPrivilege.nodes.all()
    except CypherException as e:
        return e
    for privilege in privileges:
        res = privilege.check_requirements(username)
        if not res and privilege in pleb.privileges.all():
            rel = pleb.privileges.relationship(privilege)
            if rel.active:
                rel.active = False
                rel.lost_on = datetime.now(pytz.utc)
                rel.save()
            for action in privilege.get_actions():
                rel = pleb.actions.relationship(action)
                if rel.active:
                    rel.active = False
                    rel.lost_on = datetime.now(pytz.utc)
                    rel.save()
        if not res:
            continue
        rel = pleb.privileges.connect(privilege)
        rel.save()
        for action in privilege.get_actions():
            rel = pleb.actions.connect(action)
            rel.save()
    return True