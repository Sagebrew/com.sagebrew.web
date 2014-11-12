import pytz
import logging
from json import dumps
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string

from neomodel import (StringProperty, IntegerProperty,
                      RelationshipTo,
                      BooleanProperty, FloatProperty, CypherException)

from sb_base.neo_models import SBVersioned
from sb_tag.neo_models import TagRelevanceModel


logger = logging.getLogger("loggly_logs")


class SBQuestion(SBVersioned):
    up_vote_adjustment = 5
    down_vote_adjustment = 2
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
    tags = RelationshipTo('sb_tag.neo_models.SBTag', 'TAGGED_AS')
    auto_tags = RelationshipTo('sb_tag.neo_models.SBAutoTag',
                               'AUTO_TAGGED_AS', model=TagRelevanceModel)
    closed_by = RelationshipTo('plebs.neo_models.Pleb', 'CLOSED_BY')
    answer = RelationshipTo('sb_answers.neo_models.SBAnswer',
                            'POSSIBLE_ANSWER')

    def create_relations(self, pleb, question=None, wall=None):
        try:
            rel = self.owned_by.connect(pleb)
            rel.save()
            rel_from_pleb = pleb.questions.connect(self)
            rel_from_pleb.save()
        except Exception as e:
            logger.exception(dumps({"function":
                                        SBQuestion.create_relations.__name__,
                                    "exception": "Unhandled Exception"}))
            return e

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

    def render_search(self):
        owner = self.owned_by.all()[0]
        owner_name = owner.first_name + ' ' + owner.last_name
        owner_profile_url = settings.WEB_ADDRESS + '/user/' + owner.email
        question_dict = {"question_title": self.question_title,
                         "question_content": self.content,
                         "question_uuid": self.sb_id,
                         "is_closed": self.is_closed,
                         "answer_number": self.answer_number,
                         "last_edited_on": self.last_edited_on,
                         "up_vote_number": self.up_vote_number,
                         "down_vote_number": self.down_vote_number,
                         "owner": owner_name,
                         "owner_profile_url": owner_profile_url,
                         "time_created": self.date_created,
                         "owner_email": owner.email}
        rendered = render_to_string('question_search.html', question_dict)
        return rendered

    def render_single(self):
        pass