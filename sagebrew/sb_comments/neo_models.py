from neomodel import (RelationshipTo, DateTimeProperty,
                      StructuredRel, IntegerProperty, StringProperty)

from api.neo_models import get_current_time
from sb_base.neo_models import TaggableContent


class CommentedOnRel(StructuredRel):
    shared_on = DateTimeProperty(default=get_current_time)


class Comment(TaggableContent):
    table = StringProperty(default='comments')
    up_vote_adjustment = IntegerProperty(default=2)
    down_vote_adjustment = IntegerProperty(default=-1)
    # Valid values for visibility are private and public. If this is set to
    # public any votes on the content will be counted towards reputation.
    action_name = StringProperty(default="commented on your ")
    comment_on = RelationshipTo('sb_base.neo_models.SBContent', 'COMMENT_ON')
