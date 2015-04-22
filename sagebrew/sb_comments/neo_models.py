from neomodel import (RelationshipTo, DateTimeProperty,
                      StructuredRel)

from api.neo_models import get_current_time
from sb_base.neo_models import TaggableContent


class CommentedOnRel(StructuredRel):
    shared_on = DateTimeProperty(default=get_current_time)


class Comment(TaggableContent):
    up_vote_adjustment = 2
    down_vote_adjustment = 1
    action_name = "commented on your "
    comment_on = RelationshipTo('sb_base.neo_models.SBContent', 'COMMENT_ON')
