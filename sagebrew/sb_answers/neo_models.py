from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty)

from sb_posts.neo_models import SBBase

class SBAnswer(SBBase):
    answer_id = StringProperty(unique_index=True)

    # relationships
    auto_tags = RelationshipTo('sb_tag.neo_models.SBAutoTag',
                               'AUTO_TAGGED_AS')
    answer_to = RelationshipTo('sb_questions.neo_models.SBQuestion',
                               'POSSIBLE_ANSWER_TO')
