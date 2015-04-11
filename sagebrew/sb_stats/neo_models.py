from neomodel import (IntegerProperty, CypherException)

from api.neo_models import SBObject


class SBViewCount(SBObject):
    view_count = IntegerProperty(default=0)

    def increment(self):
        try:
            self.view_count += 1
            self.save()
        except (CypherException, IOError) as e:
            return e
        return True