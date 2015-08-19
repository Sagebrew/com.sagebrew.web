from sb_base.neo_models import SBContent

from neomodel import (StringProperty, RelationshipTo, FloatProperty,
                      IntegerProperty)


class UploadedObject(SBContent):
    file_format = StringProperty()
    url = StringProperty(index=True)
    height = FloatProperty()
    width = FloatProperty()
    file_size = FloatProperty()

    # relationships
    modifications = RelationshipTo('sb_uploads.neo_models.ModifiedObject',
                                   "MODIFICATION")


class ModifiedObject(UploadedObject):
    # relationships
    modification_to = RelationshipTo('sb_uploads.neo_models.UploadedObject',
                                     'MODIFICATION_TO')


class URLContent(SBContent):
    refresh_timer = IntegerProperty(default=2) # in days
    url = StringProperty()
    description = StringProperty()
    image = StringProperty()
