import pickle
from django.conf import settings

from neomodel import (StringProperty)

from api.utils import request_to_api
from api.neo_models import SBObject


class Requirement(SBObject):
    name = StringProperty(unique_index=True)
    url = StringProperty()
    key = StringProperty()
    # gt, ge, eq, ne, ge, gt
    operator = StringProperty(default="")
    # convert to w/e type the return is
    condition = StringProperty()
    auth_type = StringProperty()

    # methods
    def check_requirement(self, username):
        # TODO need to elaborate on this
        url = str(self.url).replace("<username>", username)
        res = request_to_api(url, username, req_method='get',
                             internal=True)
        # TODO should probably handle any response greater than a 
        # 400 and stop the function as they may have the req just
        # having server issues.
        res = res.json()
        try:
            temp_type = type(res[self.key])
        except KeyError as e:
            return e
        temp_cond = temp_type(self.condition)
        return self.build_check_dict(
            pickle.loads(self.operator)(res[self.key], temp_cond),
            res[self.key])

    def build_check_dict(self, check, current):
        if check is False:
            return {"detail": False,
                    "key": self.key,
                    "operator": pickle.loads(self.operator),
                    "response": check,
                    "reason": "You must have %s %s %s, you have %s" % (
                        self.get_operator_string(), self.condition, 'flags',
                        current)}
        else:
            return {"detail": "The requirement %s was met" % (self.object_uuid),
                    "key": self.key,
                    "operator": pickle.loads(self.operator),
                    "response": check}

    def get_operator_string(self):
        return settings.OPERATOR_DICT[self.operator]