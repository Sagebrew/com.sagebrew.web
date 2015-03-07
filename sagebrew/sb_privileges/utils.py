import pytz
from datetime import datetime
from neomodel import (DoesNotExist, CypherException)

from plebs.neo_models import Pleb
from sb_docstore.utils import add_object_to_table
from sb_requirements.neo_models import SBRequirement
from .neo_models import SBPrivilege, SBAction

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
        res = privilege.check_requirements(pleb)
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
        pri_dict = privilege.get_dict()
        pri_dict.pop('requirements', None)
        pri_dict.pop('actions', None)
        pri_dict['parent_object'] = username
        res = add_object_to_table('privileges', pri_dict)
        for action in privilege.get_actions():
            rel = pleb.actions.connect(action)
            rel.save()
            act_dict = action.get_dict()
            act_dict.pop("possible_restrictions", None)
            act_dict['parent_object'] = username
            res = add_object_to_table('actions', act_dict)
    return True

def create_privilege(privilege_data, actions, requirements):
    pass