from neomodel import (StructuredNode, StringProperty, RelationshipTo)


class SBWall(StructuredNode):
    wall_id = StringProperty(unique_index=True)

    # relationships
    owner = RelationshipTo('plebs.neo_models.Pleb', 'IS_OWNED_BY')
    posts = RelationshipTo('sb_posts.neo_models.SBPost', 'HAS_POST')