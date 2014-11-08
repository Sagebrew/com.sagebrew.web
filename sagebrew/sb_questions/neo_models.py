import pytz
import logging
from json import dumps
from datetime import datetime
from neomodel import (StringProperty, IntegerProperty,
                      RelationshipTo,
                      BooleanProperty, FloatProperty, CypherException)

from sb_posts.neo_models import SBVersioned
from sb_tag.neo_models import TagRelevanceModel


logger = logging.getLogger("loggly_logs")


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
    positivity = FloatProperty()
    subjectivity = FloatProperty()
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

    def edit_content(self, pleb, content):
        from sb_questions.utils import create_question_util
        try:
            edit_question = create_question_util(content, pleb.email,
                                                     self.question_title)

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

    def edit_title(self, pleb, title):
        from sb_questions.utils import create_question_util
        try:
            edit_question = create_question_util(self.content, pleb,
                                                 title)

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

    def delete_content(self, pleb):
        try:
            self.content = ""
            self.question_title = ""
            self.to_be_deleted = True
            self.save()
        except CypherException as e:
            return e
        except Exception as e:
            logger.exception(dumps(
                {"function": SBQuestion.delete_content.__name__,
                "exception": "Unhandled Exception"}))
            return e