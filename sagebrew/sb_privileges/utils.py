import pytz
from datetime import datetime
from neomodel import (DoesNotExist, CypherException)

from plebs.neo_models import Pleb
from sb_requirements.neo_models import Requirement
from sb_requirements.serializers import RequirementSerializer

from .neo_models import Privilege, SBAction
from .serializers import ActionSerializer


def manage_privilege_relation(username):
    """
    This function checks to see if there are any privileges that a user has
    gained or lost based on the Requirements needed to obtain that privilege.
    In both cases the relationship manager is updated.

    TODO How do we track the possibility of having a Privilege multiple times?
    Do we need to add an additional node to track that? For representatives
    we could specify a date with a privilege but with core privileges we'll
    want to be able to track when someone gained/lost/and regained a privilege.
    Understand the simplicity that storing the current one off in a relationship
    manager provides. So it may be easiest to just add another node that gets
    spawned with a snapshot of the relationship when the update occurs and link
    it between the pleb and the privilege.

    If a user no longer meets the Requirements the privilege is removed.

    The function then updates the middleware to enable quicker access of the
    actions and and privileges that the user has access to.
    :param username:
    :return:
    """
    try:
        pleb = Pleb.nodes.get(username=username)
    except (CypherException, IOError) as e:
        return e
    try:
        privileges = Privilege.nodes.all()
    except(CypherException, IOError) as e:
        return e
    for item in privileges:
        print item.name
    for privilege in privileges:
        meets_reqs = privilege.check_requirements(pleb)
        print "here"
        print meets_reqs
        print privilege
        print pleb.privileges.all()
        if not meets_reqs and privilege in pleb.privileges.all():
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
            continue
        elif not meets_reqs:
            continue
        elif meets_reqs:
            rel = pleb.privileges.connect(privilege)
            rel.save()
            for action in privilege.get_actions():
                rel = pleb.actions.connect(action)
                rel.save()
    return True


def create_privilege(privilege_data, actions, requirements):
    try:
        privilege = Privilege.nodes.get(name=privilege_data["name"])
    except(Privilege.DoesNotExist, DoesNotExist):
        try:
            privilege = Privilege(**privilege_data).save()
        except (CypherException, IOError) as e:
            return e
    for action in actions:
        try:
            sb_action = SBAction.nodes.get(object_uuid=action['object_uuid'])
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
                sb_requirement = Requirement.nodes.get(
                    object_uuid=requirement['object_uuid'])
            except (Requirement.DoesNotExist, DoesNotExist) as e:
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
        Requirement.nodes.get(name=name)
        return True
    except(Requirement.DoesNotExist, DoesNotExist):
        try:
            requirement = Requirement(url=url, key=key, operator=operator,
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
        action_list.append(ActionSerializer(action).data)
    return action_list


def get_requirements():
    req_list = []
    try:
        requirements = Requirement.nodes.all()
    except (CypherException, IOError) as e:
        return e
    for req in requirements:
        req_list.append(RequirementSerializer(req).data)
    return req_list