from neomodel import (StringProperty, IntegerProperty,
                      RelationshipTo,  BooleanProperty, FloatProperty,
                      CypherException, StructuredNode)

class SBViewCount(StructuredNode):
    view_count = IntegerProperty(default=0)

    def increment(self):
        try:
            self.view_count += 1
            self.save()
        except (CypherException, IOError) as e:
            return e
        return True