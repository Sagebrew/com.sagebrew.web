import pytz
from uuid import uuid1
from datetime import datetime

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, CypherException)

from sb_base.decorators import apply_defense
from sb_base.neo_models import SBNonVersioned

class CommentedOnRel(StructuredRel):
    shared_on = DateTimeProperty(default=lambda: datetime.now(pytz.utc))


class SBComment(SBNonVersioned):
    table = 'comments'
    up_vote_adjustment = 2
    down_vote_adjustment = 1
    sb_name = "comment"
    allowed_flags = ["explicit", "spam", "other"]
    created_on = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    up_vote_number = IntegerProperty(default=0)
    down_vote_number = IntegerProperty(default=0)
    view_count = IntegerProperty(default=0)

    # relationships
    is_owned_by = RelationshipTo('plebs.neo_models.Pleb', 'OWNED_BY',
                                 model=CommentedOnRel)
    shared_by = RelationshipTo('plebs.neo_models.Pleb', 'SHARED_BY',
                               model=CommentedOnRel)
    shared_with = RelationshipTo('plebs.neo_models.Pleb', 'SHARED_WITH',
                                 model=CommentedOnRel)
    #TODO Implement the user_referenced, post_referenced, etc. relationships
    #TODO Implement referenced_by_users, referenced_by_post, etc. relationships

    def comment_on(self, comment):
        pass

    @apply_defense
    def get_single_dict(self, pleb):
        try:
            comment_owner = self.is_owned_by.all()[0]
            comment_dict = {'comment_content': self.content,
                            'comment_up_vote_number': self.get_upvote_count(),
                            'vote_count': self.get_vote_count(),
                            'sb_id': self.sb_id,
                            'comment_down_vote_number':
                                self.get_downvote_count(),
                            'comment_last_edited_on':
                                str(self.last_edited_on),
                            'comment_owner': comment_owner.first_name + ' '
                                             + comment_owner.last_name,
                            'comment_owner_email': comment_owner.email,
                            'current_user': pleb,
                            'edits': []}
            self.view_count += 1
            self.save()
            return comment_dict
        except CypherException as e:
            return e