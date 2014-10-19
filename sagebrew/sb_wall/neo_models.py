from neomodel import (StructuredNode, StringProperty, RelationshipTo,
                      One)


class SBWall(StructuredNode):
    wall_id = StringProperty(unique_index=True)

    # relationships
    owner = RelationshipTo('plebs.neo_models.Pleb', 'IS_OWNED_BY',
                           cardinality=One)
    post = RelationshipTo('sb_posts.neo_models.SBPost', 'HAS_POST')