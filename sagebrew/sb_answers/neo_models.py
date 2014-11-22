import pytz
from uuid import uuid1
from datetime import datetime
from django.conf import settings

from neomodel import (StringProperty, RelationshipTo, BooleanProperty,
                      CypherException)

from sb_base.decorators import apply_defense


from sb_base.neo_models import SBVersioned

class SBAnswer(SBVersioned):
    up_vote_adjustment = 10
    down_vote_adjustment = 10
    down_vote_cost = 2
    allowed_flags = ["explicit", "spam", "duplicate",
                     "unsupported", "other"]
    sb_name = "answer"
    added_to_search_index = BooleanProperty(default=False)
    search_id = StringProperty()

    # relationships
    auto_tags = RelationshipTo('sb_tag.neo_models.SBAutoTag',
                               'AUTO_TAGGED_AS')
    answer_to = RelationshipTo('sb_questions.neo_models.SBQuestion',
                               'POSSIBLE_ANSWER_TO')

    @apply_defense
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
            return True
        except CypherException as e:
            return e

    @apply_defense
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

    @apply_defense
    def get_single_answer_dict(self, pleb):
        try:
            answer_owner = self.owned_by.all()[0]
            answer_owner_name = answer_owner.first_name +' '+answer_owner.last_name
            answer_owner_url = answer_owner.username
            answer_dict = {'answer_content': self.content,
                           'current_pleb': pleb,
                           'answer_uuid': self.sb_id,
                           'last_edited_on': self.last_edited_on,
                           'up_vote_number': self.get_upvote_count(),
                           'down_vote_number': self.get_downvote_count(),
                           'vote_score': self.get_vote_count(),
                           'answer_owner_name': answer_owner_name,
                           'answer_owner_url': answer_owner.username,
                           'time_created': self.date_created,
                           'answer_owner_email': answer_owner.email}
            return answer_dict
        except CypherException as e:
            return e

