from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty)

from sb_posts.neo_models import SBBase

class SBQuestion(SBBase):
    question_id = StringProperty()
    has_selected_answer = BooleanProperty(default=False)
    is_closed = BooleanProperty(default=False)
    closed_reason = StringProperty()

    # relationships
    closed_by = RelationshipTo('plebs.neo_models.Pleb', 'CLOSED_BY')
    selected_answer = RelationshipTo('sb_answers.neo_models.SBAnswer', 'SELECTED_ANSWER')
    answer = RelationshipTo('sb_answers.neo_models.SBAnswer', 'POSSIBLE_ANSWER')