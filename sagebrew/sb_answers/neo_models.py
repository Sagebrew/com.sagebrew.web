import pytz
import logging
from uuid import uuid1
from json import dumps
from datetime import datetime

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, CypherException)

logger = logging.getLogger('loggly_logs')


from sb_base.neo_models import SBVersioned

class SBAnswer(SBVersioned):
    up_vote_adjustment = 10
    down_vote_adjustment = 10
    down_vote_cost = 2
    allowed_flags = ["explicit", "changed", "spam", "duplicate",
                     "unsupported", "other"]
    sb_name = "answer"
    added_to_search_index = BooleanProperty(default=False)
    search_id = StringProperty()

    # relationships
    auto_tags = RelationshipTo('sb_tag.neo_models.SBAutoTag',
                               'AUTO_TAGGED_AS')
    answer_to = RelationshipTo('sb_questions.neo_models.SBQuestion',
                               'POSSIBLE_ANSWER_TO')

    def create_relations(self, pleb, question=None, wall=None):
        try:
            self.answer_to.connect(question)
            question.answer.connect(self)
            question.answer_number += 1
            question.save()
            rel_from_pleb = pleb.answers.connect(self)
            rel_from_pleb.save()
            rel_to_pleb = self.owned_by.connect(pleb)
            rel_to_pleb.save()
            self.save()
        except Exception as e:
            logger.exception(dumps({"function":
                                        SBAnswer.create_relations.__name__,
                                    "exception": "Unhandled Exception"}))
            return e

    def edit_content(self, content, pleb):
        try:
            edit_answer = SBAnswer(sb_id=str(uuid1()), original=False,
                                   content=content).save()
            self.edits.connect(edit_answer)
            edit_answer.edit_to.connect(self)
            self.last_edited_on = datetime.now(pytz.utc)
            self.save()
            return edit_answer
        except CypherException as e:
            return e
        except Exception as e:
            return e

