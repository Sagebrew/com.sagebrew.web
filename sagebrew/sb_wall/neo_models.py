from neomodel import (StructuredNode, StringProperty, RelationshipTo)


class Wall(StructuredNode):
    wall_id = StringProperty(index=True)

    # relationships
    owned_by = RelationshipTo('plebs.neo_models.Pleb', 'IS_OWNED_BY')
    posts = RelationshipTo('sb_posts.neo_models.Post', 'HAS_POST')
