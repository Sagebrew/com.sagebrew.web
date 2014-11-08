import pytz
from uuid import uuid1
from datetime import datetime

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, CypherException)

from sb_posts.neo_models import SBVersioned

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

