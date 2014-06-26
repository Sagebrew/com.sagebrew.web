import pytz

from datetime import datetime

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, ZeroOrOne)



class CommentedOnRel(StructuredRel):
    shared_on = DateTimeProperty(default=lambda: datetime.now(pytz.utc))

class CommentVote(StructuredRel):
    up_or_down = BooleanProperty(default=None)


class SBComment(StructuredNode):
    content = StringProperty()
    comment_id = StringProperty(unique_index=True)

    #relationships
    vote = RelationshipTo('plebs.neo_models.Pleb', 'VOTE_AS', model=CommentVote)
    commented_on_post = RelationshipTo('sb_posts.neo_models.SBPost', 'COMMENTED_ON', model=CommentedOnRel)
    #commented_on_question = RelationshipTo('Question', 'COMMENTED_ON', model=CommentedOnRel)
    #commented_on_answer = RelationshipTo('Answer', 'COMMENTED_ON', model=CommentedOnRel)
    is_owned_by = RelationshipTo('plebs.neo_models.Pleb', 'OWNED_BY', model=CommentedOnRel)
    shared_by = RelationshipTo('plebs.neo_models.Pleb', 'SHARED_BY', model=CommentedOnRel)
    shared_with = RelationshipTo('plebs.neo_models.Pleb', 'SHARED_WITH', model=CommentedOnRel)
    #TODO Implement the user_referenced, post_referenced, etc. relationships
    flagged_by = RelationshipTo('plebs.neo_models.Pleb', 'FLAGGED_BY', model=CommentedOnRel)
    #TODO Implement referenced_by_users, referenced_by_post, etc. relationships