from uuid import uuid1

from neomodel import (StringProperty, IntegerProperty, CypherException,
                      StructuredNode)


class SBViewCount(StructuredNode):
    object_uuid = StringProperty(unique_index=True, default=str(uuid1()))
    view_count = IntegerProperty(default=0)

    def increment(self):
        try:
            self.view_count += 1
            self.save()
        except (CypherException, IOError) as e:
            return e
        return True