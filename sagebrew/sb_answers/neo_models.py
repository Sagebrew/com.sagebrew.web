from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty)

from sb_posts.neo_models import SBBase

class SBAnswer(SBBase):
    answer_id = StringProperty()
    selected_answer = BooleanProperty(default=False)

    # relationships
    possible_answer_to = RelationshipTo('sb_questions.neo_models.SBQuestion', 'POSSIBLE_ANSWER_TO')
    selected_answer_to = RelationshipTo('sb_questions.neo_models.SBQuestion', 'SELECTED_ANSWER_TO')