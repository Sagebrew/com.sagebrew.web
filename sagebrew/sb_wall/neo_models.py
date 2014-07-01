import pytz

from datetime import datetime

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, ZeroOrOne)


class SBWall(StructuredNode):
    wall_id = StringProperty(unique_index=True)

    #relationships
    owner = RelationshipTo('plebs.neo_models.Pleb', 'IS_OWNED_BY')
    post = RelationshipTo('sb_posts.neo_models.SBPost', 'HAS_POST')