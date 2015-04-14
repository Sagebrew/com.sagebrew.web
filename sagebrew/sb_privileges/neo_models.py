import pytz
import pickle
from datetime import datetime
from neomodel import (StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, BooleanProperty)

from api.utils import request_to_api
from api.neo_models import SBObject


class Privilege(SBObject):
    name = StringProperty(unique_index=True)

    # relationships
    actions = RelationshipTo('sb_privileges.neo_models.SBAction', 'GRANTS')
    requirements = RelationshipTo('sb_requirements.neo_models.Requirement',
                                  'REQUIRES')
    badges = RelationshipTo('sb_badges.neo_models.BadgeBase', "REQUIRES_BADGE")

    def check_requirements(self, pleb):
        for req in self.get_requirements():
            req_response = req.check_requirement(pleb.username)
            if isinstance(req_response, Exception):
                return False
            if req_response['detail'] is False:
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


class SBAction(SBObject):
    resource = StringProperty(index=True)
    # If a user has write permission we assume they have read as well
    # this may change in the future but that should only require a search
    # for all write permissions and change to read/write or association of
    # read actions with the user. Write = POST, Read = GET, and PUT/PATCH can
    # always be performed by the user on their own content
    permission = StringProperty()
    url = StringProperty(index=True)

    # relationships
    privilege = RelationshipTo('sb_privileges.neo_models.Privilege',
                               'PART_OF')
    restrictions = RelationshipTo('sb_privileges.neo_models.Restriction',
                                  'RESTRICTED_BY')

    def get_restrictions(self):
        return self.restrictions.all()


class Restriction(SBObject):
    base = BooleanProperty(default=False)
    name = StringProperty(unique_index=True)
    url = StringProperty()
    key = StringProperty()
    operator = StringProperty(default="")  # gt, ge, eq, ne, ge, gt
    condition = StringProperty()  # convert to w/e type the return is
    auth_type = StringProperty()
    expiry = IntegerProperty()  # time in seconds until the restriction is up
    end_date = DateTimeProperty()
    recurring = BooleanProperty(default=False)

    def check_restriction(self, username, start_date):
        res = request_to_api(self.url, username, req_method='get',
                             internal=True)
        # TODO should probably handle any response greater than a
        # 400 and stop the function as they may have the req just
        # having server issues.
        res = res.json()
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
                    "reason": "You must have %s %s %s, you have %s" % (
                        self.get_operator_string(), self.condition, 'flags',
                        current)}
        else:
            return {"detail": "The restriction %s was met" % (self.object_uuid),
                    "key": self.key,
                    "operator": pickle.loads(self.operator),
                    "response": check}
