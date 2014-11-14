import pytz
import logging
from json import dumps
from datetime import datetime
from api.utils import execute_cypher_query
from django.conf import settings
from django.template import Context
from django.template.loader import render_to_string, get_template

from neomodel import (StringProperty, IntegerProperty,
                      RelationshipTo, db,
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
        print pleb.email
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
        except (CypherException, AttributeError) as e:
            return e
        except Exception as e:
            logger.exception(dumps({"function":
                                        SBQuestion.edit_content.__name__,
                                    "exception": "Unhandled Exception"}))
            return e

    def edit_title(self, pleb, title):
        from sb_questions.utils import create_question_util
        try:
            edit_question = create_question_util(self.content, pleb.email,
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
            logger.exception(dumps({'function': SBQuestion.edit_title.__name__,
                                    'exception': 'Unhandled Exception'}))
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

    def get_single_question_dict(self, pleb):
        from sb_answers.neo_models import SBAnswer
        try:
            answer_array = []
            owner = self.owned_by.all()
            owner = owner[0]
            owner_name = owner.first_name + ' ' + owner.last_name
            owner_profile_url = settings.WEB_ADDRESS + '/user/' + owner.email
            query = 'match (q:SBQuestion) where q.sb_id="%s" ' \
                    'with q ' \
                    'match (q)-[:POSSIBLE_ANSWER]-(a:SBAnswer) ' \
                    'where a.to_be_deleted=False ' \
                    'return a ' % self.sb_id
            answers, meta = execute_cypher_query(query)
            answers = [SBAnswer.inflate(row[0]) for row in answers]
            for answer in answers:
                answer_array.append(answer.get_single_answer_dict(pleb))
            question_dict = {'question_title': self.question_title,
                             'question_content': self.content,
                             'question_uuid': self.sb_id,
                             'is_closed': self.is_closed,
                             'answer_number': self.answer_number,
                             'last_edited_on': self.last_edited_on,
                             'up_vote_number': self.get_upvote_count(),
                             'down_vote_number': self.get_downvote_count(),
                             'vote_score': self.get_vote_count(),
                             'owner': owner_name,
                             'owner_profile_url': owner_profile_url,
                             'time_created': self.date_created,
                             'answers': answer_array,
                             'current_pleb': pleb,
                             'owner_email': owner.email}
            return question_dict
        except Exception as e:
            logger.exception(dumps({'function':
                                        SBQuestion.get_single_question_dict.__name__,
                                    'exception': 'Unhandled Exception'}))
            return e

    def get_multiple_question_dict(self, pleb):
        try:
            owner = self.owned_by.all()
            owner = owner[0]
            owner = owner.first_name + ' ' + owner.last_name
            question_dict = {'question_title': self.question_title,
                             'question_content': self.content[:50]+'...',
                             'is_closed': self.is_closed,
                             'answer_number': self.answer_number,
                             'last_edited_on': self.last_edited_on,
                             'up_vote_number': self.up_vote_number,
                             'down_vote_number': self.down_vote_number,
                             'owner': owner,
                             'time_created': self.date_created,
                             'question_url': settings.WEB_ADDRESS +
                                             '/questions/' +
                                             self.sb_id,
                             'current_pleb': pleb
                        }
            return question_dict
        except Exception as e:
            logger.exception(dumps({'function':
                                        SBQuestion.get_multiple_question_dict.__name__,
                                    'exception': 'Unhandled Exception'}))
            return e

    def render_question_page(self, pleb):
        try:
            owner = self.owned_by.all()
            owner = owner[0]
            owner = owner.first_name + ' ' + owner.last_name
            question_dict = {'question_title': self.question_title,
                             'question_content': self.content[:50]+'...',
                             'is_closed': self.is_closed,
                             'answer_number': self.answer_number,
                             'last_edited_on': self.last_edited_on,
                             'up_vote_number': self.up_vote_number,
                             'down_vote_number': self.down_vote_number,
                             'owner': owner,
                             'time_created': self.date_created,
                             'question_url': settings.WEB_ADDRESS +
                                             '/questions/' +
                                             self.sb_id,
                             'current_pleb': pleb
                        }
            t = get_template("questions.html")
            c = Context(question_dict)
            return t.render(c)
        except Exception:
            logger.exception(dumps({'function':
                                        SBQuestion.render_question_page.__name__,
                                    'exception': "Unhandled Exception"}))
            return ''

    def render_search(self):
        try:
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
        except Exception as e:
            logger.exception(dumps({'function': SBQuestion.render_search.__name__,
                                    'exception': 'Unhandled Exception'}))
            return e

    def render_single(self, pleb):
        try:
            t = get_template("single_question.html")
            c = Context(self.get_single_question_dict(pleb))
            return t.render(c)
        except Exception as e:
            logger.exception(dumps({'function': SBQuestion.render_single.__name__,
                                    'exception': 'Unhandled Exception'}))
            return e

    def render_multiple(self, pleb):
        pass