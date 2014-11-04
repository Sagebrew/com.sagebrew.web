from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty)

from sb_posts.neo_models import SBVersioned

class SBAnswer(SBVersioned):
    allowed_flags = ["explicit", "changed", "spam", "duplicate",
                     "unsupported", "other"]
    sb_name = "answer"
    added_to_search_index = BooleanProperty(default=False)
    search_id = StringProperty()

    # relationships
    edits = RelationshipTo('sb_answers.neo_models.SBAnswer', 'EDIT')
    edit_to = RelationshipTo('sb_answers.neo_models.SBAnswer', 'EDIT_TO')
    auto_tags = RelationshipTo('sb_tag.neo_models.SBAutoTag',
                               'AUTO_TAGGED_AS')
    answer_to = RelationshipTo('sb_questions.neo_models.SBQuestion',
                               'POSSIBLE_ANSWER_TO')
