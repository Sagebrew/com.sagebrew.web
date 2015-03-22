from uuid import uuid1

from sb_base.decorators import apply_defense
from sb_base.neo_models import SBContent

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, CypherException,
                      RelationshipFrom, DoesNotExist, DateProperty)

class Image(SBContent):
    url = StringProperty()

    #relationships
    sizes = RelationshipTo('sb_uploads.neo_models.SubImage', "RESIZE")

class SubImage(SBContent):
    object_uuid = StringProperty(unique_index=True)
    url = StringProperty()
    height = IntegerProperty()
    width = IntegerProperty()
    file_size = FloatProperty()


