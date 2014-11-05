import pytz
from datetime import datetime
from neomodel import (StringProperty, IntegerProperty,
                      RelationshipTo,
                      BooleanProperty, FloatProperty, CypherException)

from sb_posts.neo_models import SBVersioned
from sb_tag.neo_models import TagRelevanceModel


class SBQuestion(SBVersioned):
    allowed_flags = ["explicit", "changed", "spam", "duplicate",
                     "unsupported", "other"]
    answer_number = IntegerProperty(default=0)
    question_title = StringProperty()
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
    answer = RelationshipTo('sb_answers.neo_models.SBAnswer',
                            'POSSIBLE_ANSWER')

    def edit_content(self, pleb, content=None, question_title=None):
        from sb_questions.utils import create_question_util
        try:
            if question_title is None and content is None:
                return False
            elif question_title is not None and content is None:
                edit_question = create_question_util(self.content, pleb,
                                                     self.question_title)
            elif question_title is None and content is not None:
                edit_question = create_question_util(content, pleb,
                                                     self.question_title)
            else:
                edit_question = create_question_util(content, pleb,
                                                     question_title)

            if isinstance(edit_question, Exception) is True:
                return edit_question
            edit_question.original = False
            edit_question.save()
            self.edits.connect(edit_question)
            edit_question.edit_to.connect(self)
            self.last_edited_on = datetime.now(pytz.utc)
            self.save()
            return edit_question
        except CypherException as e:
            return e
        except Exception as e:
            return e
