from neomodel import (StructuredNode, StringProperty, RelationshipTo)


class Wall(StructuredNode):
    wall_id = StringProperty(unique_index=True)

    # relationships
    owned_by = RelationshipTo('sagebrew.plebs.neo_models.Pleb', 'IS_OWNED_BY')
    posts = RelationshipTo('sagebrew.sb_posts.neo_models.Post', 'HAS_POST')
