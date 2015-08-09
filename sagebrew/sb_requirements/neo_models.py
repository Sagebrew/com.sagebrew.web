import pickle
import operator
from django.conf import settings

from rest_framework import status

from neomodel import StringProperty

from api.utils import request_to_api
from api.neo_models import SBObject


class Requirement(SBObject):
    name = StringProperty(unique_index=True)
    # url has some special operations taken on it before it is utilized.
    # currently the value <username> is replaced with the actual username of
    # the user who is having requirements check on their behalf. This may
    # expand in the future.
    url = StringProperty()
    key = StringProperty()
    # see base.py OPERATOR_TYPES for supported types
    # We utilize python's pickle and operator libraries to manage these
    # strings.
    operator = StringProperty()
    # convert to w/e type the return is
    condition = StringProperty()
    auth_type = StringProperty()

    def check_requirement(self, username):
        """
        check_requirement is responsible for determining if a defined criteria
        has been met by a given user, defined by their unique username.

        The method utilizes the a defined url to query a JSON object from
        some endpoint and compare a value associated with a specific key from
        that object with the condition stored in the object.

        :param username: Unique identifier corresponding to a given user and
        profile
        :return:
        """
        url = str(self.url).replace("<username>", username)
        res = request_to_api(url, username, req_method='get')
        if res.status_code >= status.HTTP_400_BAD_REQUEST:
            raise IOError("%d" % res.status_code)
        res = res.json()
        try:
            temp_type = type(res[self.key])
        except KeyError as e:
            return e
        temp_cond = temp_type(self.condition)
        operator_holder = pickle.loads(self.operator)
        if (operator_holder is operator.not_ or
                operator_holder is operator.truth):
            self.build_check_dict(operator_holder(res[self.key]),
                                  res[self.key])
        return self.build_check_dict(operator_holder(res[self.key], temp_cond),
                                     res[self.key])

    def build_check_dict(self, check, current):
        if check is False:
            return {
                "detail": False,
                "key": self.key,
                "operator": pickle.loads(self.operator),
                "response": check,
                "reason": "You must have %s %s, you have %s to gain the %s "
                          "Privilege." % (
                    self.get_operator_string(), self.condition, current,
                    self.name)
            }
        else:
            return {
                "detail": "The requirement %s was met" % self.object_uuid,
                "key": self.key,
                "operator": pickle.loads(self.operator),
                "response": check
            }

    def get_operator_string(self):
        return settings.OPERATOR_DICT[self.operator]
