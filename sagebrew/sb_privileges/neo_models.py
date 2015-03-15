import pytz
import pickle
from uuid import uuid1
from datetime import datetime

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, BooleanProperty)

from api.utils import post_to_api


class SBPrivilege(StructuredNode):
    sb_id = StringProperty(default=lambda: str(uuid1()))
    name = StringProperty(unique_index=True)

    #relationships
    actions = RelationshipTo('sb_privileges.neo_models.SBAction', 'GRANTS')
    requirements = RelationshipTo('sb_requirements.neo_models.SBRequirement',
                                  'REQUIRES')
    badges = RelationshipTo('sb_badges.neo_models.BadgeBase', "REQUIRES_BADGE")

    def check_requirements(self, pleb):
        req_checks = []
        for req in self.get_requirements():
            req_checks.append(req.check_requirement(pleb.username)['response'])
        if False in req_checks:
            return False
        return True

    def check_badges(self, pleb):
        for badge in pleb.get_badges():
            if badge not in self.badges.all():
                return False
        return True

    def get_requirements(self):
        return self.requirements.all()

    def get_actions(self):
        return self.actions.all()

    def get_dict(self):
        actions = []
        requirements = []
        for action in self.get_actions():
            actions.append(action.get_dict)
        for req in self.get_requirements():
            requirements.append(req.get_dict())
        return {
            "sb_id": self.sb_id,
            "name": self.name,
            "actions": actions,
            "requirements": requirements,
            "privilege": self.name
        }


class SBAction(StructuredNode):
    sb_id = StringProperty(default=lambda: str(uuid1()))
    action = StringProperty(default="")
    object_type = StringProperty()#one of the object types specified in settings.KNOWN_TYPES
    url = StringProperty()
    html_object = StringProperty()

    #relationships
    privilege = RelationshipTo('sb_privileges.neo_models.SBPrivilege',
                               'PART_OF')
    restrictions = RelationshipTo('sb_privileges.neo_models.SBRestriction',
                                  'RESTRICTED_BY')

    def get_dict(self):
        possible_restrictions = []
        for restriction in self.get_restrictions():
            possible_restrictions.append(restriction.get_dict)
        return {"sb_id": self.sb_id,
                "action": self.action,
                "object_type": self.object_type,
                "url": self.url,
                "html_object": self.html_object,
                "possible_restrictions": possible_restrictions}

    def get_restrictions(self):
        return self.restrictions.all()


class SBRestriction(StructuredNode):
    sb_id = StringProperty(default=lambda: str(uuid1()), unique_index=True)
    base = BooleanProperty(default=False)
    name = StringProperty(unique_index=True)
    url = StringProperty()
    key = StringProperty()
    operator = StringProperty(default="") #gt, ge, eq, ne, ge, gt
    condition = StringProperty() #convert to w/e type the return is
    auth_type = StringProperty()
    expiry = IntegerProperty() #time in seconds until the restriction is up
    end_date = DateTimeProperty()
    recurring = BooleanProperty(default=False)

    #methods
    def get_dict(self):
        return {
            "sb_id": self.sb_id,
            "restriction": self.name,
            "key": self.key,
            "operator": self.operator,
            "condition": self.condition,
            "auth_type": self.auth_type,
            "end_date": self.end_date,
            "expiry": self.restriction_expiry,
            "url": self.url
        }

    def check_restriction(self, username, start_date):
        res = post_to_api(self.url, username, req_method='get')
        temp_type = type(res[self.key])
        temp_cond = temp_type(self.condition)
        return self.build_check_dict(
            pickle.loads(self.operator)(res[self.key], temp_cond),
            res[self.key])

    def build_check_dict(self, check, current):
        if not self.expiry <= (datetime.now(pytz.utc) - self.end_date).seconds:
            check = False
        if not check:
            return {"detail": False,
                    "key": self.key,
                    "operator": pickle.loads(self.operator),
                    "response": check,
                    "reason": "You must have %s %s %s, you have %s"%(
                        self.get_operator_string(), self.condition, 'flags',
                        current)}
        else:
            return {"detail": "The restriction %s was met"%(self.sb_id),
                    "key": self.key,
                    "operator": pickle.loads(self.operator),
                    "response": check}

