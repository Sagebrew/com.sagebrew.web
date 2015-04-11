from uuid import uuid1

from neomodel import (StructuredNode, StringProperty)


class SBObject(StructuredNode):
    object_uuid = StringProperty(default=uuid1, unique_index=True)