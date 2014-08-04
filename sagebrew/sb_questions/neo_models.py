from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty)

from sb_posts.neo_models import SBBase

class SBQuestion(SBBase):
    answer_number = IntegerProperty(default=0)
    question_title = StringProperty()
    question_id = StringProperty()
    is_closed = BooleanProperty(default=False)
    closed_reason = StringProperty()

    # relationships
    closed_by = RelationshipTo('plebs.neo_models.Pleb', 'CLOSED_BY')
    answer = RelationshipTo('sb_answers.neo_models.SBAnswer', 'POSSIBLE_ANSWER')