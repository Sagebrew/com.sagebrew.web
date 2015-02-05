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

    def check_requirements(self, username):
        req_checks = []
        for req in self.get_requirements():
            req_checks.append(req.check_requirement(username)['response'])
        if False in req_checks:
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
            "requirements": requirements
        }




class SBAction(StructuredNode):
    sb_id = StringProperty(default=lambda: str(uuid1()))
    action = StringProperty(default="read")
    object_type = StringProperty()#one of the object types specified in settings.KNOWN_TYPES
    url = StringProperty()


    #relationships
    privilege = RelationshipTo('sb_privileges.neo_models.SBPrivilege',
                               'PART_OF')

    def get_dict(self):
        return {"sb_id": self.sb_id,
                "action_type": self.action,
                "object_type": self.object_type,
                "url": self.url}