from sb_base.neo_models import SBContent

from neomodel import (StringProperty, IntegerProperty, RelationshipTo,
                      FloatProperty)


class Image(SBContent):
    url = StringProperty()

    # relationships
    sizes = RelationshipTo('sb_uploads.neo_models.SubImage', "RESIZE")


class SubImage(SBContent):
    object_uuid = StringProperty(unique_index=True)
    url = StringProperty()
    height = IntegerProperty()
    width = IntegerProperty()
    file_size = FloatProperty()
