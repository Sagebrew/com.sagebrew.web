from sb_base.neo_models import SBContent

from neomodel import (StringProperty, RelationshipTo, FloatProperty,
                      IntegerProperty, db)


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
    url = StringProperty(unique_index=True)
    description = StringProperty()
    selected_image = StringProperty()

    images = RelationshipTo('sb_uploads.neo_models.UploadedObject',
                            'IMAGE_ON_PAGE')

    def get_images(self):
        query = 'MATCH (a:URLContent {object_uuid:"%s"})-[:IMAGE_ON_PAGE]->' \
                '(b:UploadedObject) RETURN b.object_uuid' % self.object_uuid
        res, col = db.cypher_query(query)
        return [row[0] for row in res]
