from neomodel import (RelationshipTo, DateTimeProperty, db,
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
    parent_type = StringProperty()
    parent_id = StringProperty()
    comment_on = RelationshipTo('sb_base.neo_models.SBContent', 'COMMENT_ON')

    @classmethod
    def get_comment_on(cls, object_uuid):
        from sb_base.neo_models import SBContent
        query = 'MATCH (c:Comment {object_uuid:"%s"})<-[:HAS_A]-(o) ' \
                'RETURN o' % object_uuid
        res, _ = db.cypher_query(query)
        return SBContent.inflate(res.one)

    @classmethod
    def get_mission(cls, object_uuid, request):
        from sb_solutions.neo_models import Solution
        from sb_questions.neo_models import Question
        comment = Comment.nodes.get(object_uuid=object_uuid)
        if comment.parent_type == "solution":
            return Solution.get_mission(comment.parent_id, request)
        elif comment.parent_type == "question":
            return Question.get_mission(comment.parent_id, request)
        else:
            return None
