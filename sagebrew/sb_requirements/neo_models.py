import pickle
from uuid import uuid1
from django.conf import settings

from neomodel import (StructuredNode, StringProperty)

from api.utils import request_to_api


class SBRequirement(StructuredNode):
    sb_id = StringProperty(default=lambda: str(uuid1()), unique_index=True)
    name = StringProperty(unique_index=True)
    url = StringProperty()
    key = StringProperty()
    # gt, ge, eq, ne, ge, gt
    operator = StringProperty(default="")
    # convert to w/e type the return is
    condition = StringProperty()
    auth_type = StringProperty()

    #methods
    def check_requirement(self, username):
        res = request_to_api(self.url, username, req_method='get')
        temp_type = type(res[self.key])
        temp_cond = temp_type(self.condition)
        return self.build_check_dict(
            pickle.loads(self.operator)(res[self.key], temp_cond),
            res[self.key])

    def build_check_dict(self, check, current):
        if not check:
            return {"detail": False,
                    "key": self.key,
                    "operator": pickle.loads(self.operator),
                    "response": check,
                    "reason": "You must have %s %s %s, you have %s" % (
                        self.get_operator_string(), self.condition, 'flags',
                        current)}
        else:
            return {"detail": "The requirement %s was met" % (self.sb_id),
                    "key": self.key,
                    "operator": pickle.loads(self.operator),
                    "response": check}

    def get_dict(self):
        return {"req_id": self.sb_id,
                "url": self.url,
                "key": self.key,
                "operator": self.operator,
                "condition": self.condition}

    def get_operator_string(self):
        return settings.OPERATOR_DICT[self.operator]