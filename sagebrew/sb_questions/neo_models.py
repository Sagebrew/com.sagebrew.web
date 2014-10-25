from neomodel import (StringProperty, IntegerProperty,
                      RelationshipTo,
                      BooleanProperty, FloatProperty)

from sb_posts.neo_models import SBBase
from sb_tag.neo_models import TagRelevanceModel


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
    search_id = StringProperty()
    tags_added = BooleanProperty(default=False)
    added_to_search_index = BooleanProperty(default=False)

    # relationships
    edits = RelationshipTo('sb_questions.neo_models.SBQuestion', 'EDIT')
    edit_to = RelationshipTo('sb_questions.neo_models.SBQuestion', 'EDIT_TO')
    tags = RelationshipTo('sb_tag.neo_models.SBTag', 'TAGGED_AS')
    auto_tags = RelationshipTo('sb_tag.neo_models.SBAutoTag',
                               'AUTO_TAGGED_AS', model=TagRelevanceModel)
    closed_by = RelationshipTo('plebs.neo_models.Pleb', 'CLOSED_BY')
    answer = RelationshipTo('sb_answers.neo_models.SBAnswer', 'POSSIBLE_ANSWER')
