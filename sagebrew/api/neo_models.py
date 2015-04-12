from uuid import uuid1

from neomodel import (StructuredNode, StringProperty)


class SBObject(StructuredNode):
    __abstract_node__ = True

    object_uuid = StringProperty(default=uuid1, unique_index=True)