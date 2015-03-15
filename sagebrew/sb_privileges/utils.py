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
    try:
        privilege = SBPrivilege.nodes.get(name=privilege_data["name"])
    except(SBPrivilege.DoesNotExist, DoesNotExist):
        try:
            privilege = SBPrivilege(**privilege_data).save()
        except (CypherException, IOError) as e:
            return e
    for action in actions:
        try:
            sb_action = SBAction.nodes.get(sb_id=action['object_uuid'])
        except (CypherException, IOError, SBAction.DoesNotExist,
                DoesNotExist) as e:
            return e
        try:
            privilege.actions.connect(sb_action)
            sb_action.privilege.connect(privilege)
        except (CypherException, IOError) as e:
            return e
    for requirement in requirements:
        try:
            try:
                sb_requirement = SBRequirement.nodes.get(
                    sb_id=requirement['object_uuid'])
            except (SBRequirement.DoesNotExist, DoesNotExist) as e:
                return e
            privilege.requirements.connect(sb_requirement)
        except (CypherException, IOError) as e:
            return e
    return True


def create_action(action, object_type, url, html_object=None):
    try:
        SBAction.nodes.get(action=action["action"])
        return True
    except(SBAction.DoesNotExist, DoesNotExist):
        try:
            action = SBAction(action=action, object_type=object_type, url=url,
                              html_object=html_object)
            action.save()
        except (CypherException, IOError) as e:
            return e
    return True


def create_requirement(url, key, operator, condition, name, auth_type=None):
    try:
        SBRequirement.nodes.get(name=name)
        return True
    except(SBRequirement.DoesNotExist, DoesNotExist):
        try:
            requirement = SBRequirement(url=url, key=key, operator=operator,
                                        condition=condition, auth_type=auth_type,
                                        name=name)
            requirement.save()
        except (CypherException, IOError) as e:
            return e
    return True


def get_actions():
    action_list = []
    try:
        actions = SBAction.nodes.all()
    except (CypherException, IOError) as e:
        return e
    for action in actions:
        action_list.append(action.get_dict())
    return action_list


def get_requirements():
    req_list = []
    try:
        requirements = SBRequirement.nodes.all()
    except (CypherException, IOError) as e:
        return e
    for req in requirements:
        req_list.append(req.get_dict())
    return req_list