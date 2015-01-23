import pickle
import urllib2
from uuid import uuid1

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, CypherException,
                      RelationshipFrom, DoesNotExist, JSONProperty)

class Requirement(StructuredNode):
    sb_id = StringProperty(default=lambda: str(uuid1()), unique_index=True)
    url = StringProperty()
    key = StringProperty()
    operator = StringProperty(default="") #gt, ge, eq, ne, ge, gt
    condition = StringProperty() #convert to w/e type the return is

    #methods
    def check_requirement(self):
        req = urllib2.Request(self.url)
        res = urllib2.urlopen(req)
        data = res.read()
        temp_type = type(data[self.key])
        temp_cond = temp_type(self.condition)
        return self.build_check_dict(
            pickle.loads(self.operator)(data[self.key], temp_cond))

    def build_check_dict(self, check):
        if not check:
            return {"detail": "The requirement %s was not met"%(self.sb_id),
                    "key": self.key,
                    "operator": pickle.loads(self.operator),
                    "response": check,
                    "reason": "You must have %s %s %s, you have %s"%('less than', '4', 'flags', '7')}#sample layout for the response sentence construction

    def get_dict(self):
        return {"req_id": self.sb_id,
                "url": self.url,
                "key": self.key,
                "operator": self.operator,
                "condition": self.condition}
