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
        try:
            res = res.json()
        except ValueError:
            return {
                "detail": "We're sorry we cannot check this requirement. "
                          "It looks like the url you're checking doesn't return"
                          " a JSON response.",
                "response": False
            }
        try:
            temp_type = type(res[self.key])
        except KeyError:
            return {
                "detail": "We're sorry we cannot check this requirement. "
                          "The key cannot be found in the response we received "
                          "from the server.",
                "response": False
            }
        try:
            if self.condition is not None:
                try:
                    temp_cond = temp_type(self.condition)
                except TypeError:
                    return {
                        "detail": "We're sorry we cannot check this "
                                  "requirement. We cannot compare a null "
                                  "type in this case. Please try using 'is not'"
                                  " instead.",
                        "response": False
                    }
            else:
                temp_cond = self.condition
        except ValueError:
            return {
                "detail": "We're sorry we cannot check this requirement. The"
                          " condition is not the same type as the value it's "
                          "being compared to.",
                "response": False
            }
        try:
            operator_holder = pickle.loads(self.operator)
        except IndexError:
            return {
                "detail": "We're sorry we cannot check this requirement. The"
                          " operator does not seem to be valid.",
                "response": False
            }
        if (operator_holder is operator.not_ or
                operator_holder is operator.truth):
            return self.build_check_dict(operator_holder(res[self.key]),
                                         res[self.key])
        return self.build_check_dict(operator_holder(res[self.key], temp_cond),
                                     res[self.key])

    def build_check_dict(self, check, current):
        if check is False:
            return {
                "detail": "You have %s %s, %s must be %s %s to gain "
                          "the %s Privilege." % (current, self.key, self.key,
                                                 self.get_operator_string(),
                                                 self.condition, self.name),
                "key": self.key,
                "operator": self.get_operator_string(),
                "response": check
            }
        else:
            return {
                "detail": "The requirement %s was met" % self.name,
                "key": self.key,
                "operator": self.get_operator_string(),
                "response": check
            }

    def get_operator_string(self):
        return settings.OPERATOR_DICT[self.operator]
