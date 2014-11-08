from neomodel import (StructuredNode, StringProperty, RelationshipTo)


class SBFlag(StructuredNode):
    flag_type = StringProperty(unique_index=True)
