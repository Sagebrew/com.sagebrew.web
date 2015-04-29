from neomodel import (StructuredNode, StringProperty, RelationshipTo)
from neomodel import db

from plebs.neo_models import Pleb


class Wall(StructuredNode):
    wall_id = StringProperty(unique_index=True)

    # relationships
    owned_by = RelationshipTo('plebs.neo_models.Pleb', 'IS_OWNED_BY')
    posts = RelationshipTo('sb_posts.neo_models.Post', 'HAS_POST')

    def get_owned_by(self):
        '''
        Cypher Exception and IOError excluded on purpose, please do not add.
        The functions calling this expect the exceptions to be thrown and
        handle the exceptions on their own if they end up occuring.
        :return:
        '''
        query = "MATCH (a:Wall {wall_id:'%s'})-" \
                "[:IS_OWNED_BY]->(b:Pleb) RETURN b" % (self.wall_id)
        res, col = db.cypher_query(query)
        try:
            return Pleb.inflate(res[0][0])
        except IndexError:
            return None