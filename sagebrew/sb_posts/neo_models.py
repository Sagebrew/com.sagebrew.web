from rest_framework.reverse import reverse

from neomodel import (RelationshipTo, StringProperty, db)

from sb_base.neo_models import SBPrivateContent
from plebs.neo_models import Pleb


class Post(SBPrivateContent):
    table = StringProperty(default='posts')
    action_name = StringProperty(default="posted on your wall")

    # relationships
    posted_on_wall = RelationshipTo('sb_wall.neo_models.Wall', 'POSTED_ON')

    def get_url(self, request=None):
        return reverse('profile_page', kwargs={
            'pleb_username': self.get_wall_owner_profile().username
        }, request=request)

    def get_wall_owner_profile(self):
        query = "MATCH (a:Post {object_uuid: '%s'})-[:POSTED_ON]->(b:Wall)-" \
                "[:IS_OWNED_BY]->(c:Pleb) RETURN c" % self.object_uuid
        res, col = db.cypher_query(query)
        return Pleb.inflate(res.one)
