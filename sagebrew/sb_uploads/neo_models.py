from sb_base.neo_models import SBContent

from neomodel import (StringProperty, IntegerProperty, RelationshipTo,
                      FloatProperty)


class UploadedObject(SBContent):
    """
    We could use imghdr https://docs.python.org/2/library/imghdr.html or
    python magic to determine what the file type is but we've choosen to go
    with python magic as it's more expandable. We could potentially utilize
    imghdr in a child class specific to images.
    """
    media_type = StringProperty()
    url = StringProperty()

    # relationships
    sizes = RelationshipTo('sb_uploads.neo_models.SubImage', "RESIZE")


class SubImage(SBContent):
    url = StringProperty()
    height = IntegerProperty()
    width = IntegerProperty()
    file_size = FloatProperty()
