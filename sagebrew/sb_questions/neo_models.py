from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty)

from sb_posts.neo_models import SBBase

class SBQuestion(SBBase):
    answer_number = IntegerProperty(default=0)
    question_title = StringProperty()
    question_id = StringProperty(unique_index=True)
    is_closed = BooleanProperty(default=False)
    closed_reason = StringProperty()
    is_private = BooleanProperty()
    is_protected = BooleanProperty(default=False)
    is_mature = BooleanProperty(default=False)
    title_polarity = FloatProperty()
    title_subjectivity = FloatProperty()

    # relationships
    closed_by = RelationshipTo('plebs.neo_models.Pleb', 'CLOSED_BY')
    answer = RelationshipTo('sb_answers.neo_models.SBAnswer', 'POSSIBLE_ANSWER')
