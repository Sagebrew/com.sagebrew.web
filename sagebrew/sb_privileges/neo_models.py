from uuid import uuid1
from django.conf import settings

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, CypherException,
                      RelationshipFrom, DoesNotExist, JSONProperty)

class SBPrivilege(StructuredNode):
    sb_id = StringProperty(default=lambda: str(uuid1()))
    privilege_name = StringProperty()

    #relationships
    actions = RelationshipTo('sb_privileges.neo_models.SBAction', 'GRANTS')
    requirements = RelationshipTo('sb_requirements.neo_models.Requirement',
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
            "name": self.privilege_name,
            "actions": actions,
            "requirements": requirements,
            "privilege": self.privilege_name
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
    sb_id = StringProperty(default=lambda: str(uuid1()))
    res_type = StringProperty()
    limit = IntegerProperty()
    time_limit = DateTimeProperty()
    expiry = DateTimeProperty()
    current = IntegerProperty()
    url = StringProperty()

    #methods
    def get_dict(self):
        return {
            "sb_id": self.sb_id,
            "restriction": self.restriction_type,
            "restriction_limit": self.restriction_limit,
            "restriction_time_limit": self.restriction_time_limit,
            "restriction_expiry": self.restriction_expiry,
            "current": self.current,
            "url": self.url
        }