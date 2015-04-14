import pytz
from uuid import uuid1
from datetime import datetime

from neomodel import (StringProperty, RelationshipTo,
                      CypherException)

from sb_base.decorators import apply_defense


from sb_base.neo_models import SBPublicContent


class Solution(SBPublicContent):
    object_type = "02241aee-644f-11e4-9ad9-080027242395"
    table = 'public_solutions'
    action_name = "offered a solution to a question"
    up_vote_adjustment = 10
    down_vote_adjustment = 10
    down_vote_cost = 2
    search_id = StringProperty()

    # relationships
    solution_to = RelationshipTo('sb_questions.neo_models.Question',
                                 'POSSIBLE_ANSWER_TO')

    @apply_defense
    def create_relations(self, pleb, question=None, wall=None):
        if question is None:
            return False
        try:
            self.solution_to.connect(question)
            question.solutions.connect(self)
            question.solution_count += 1
            question.save()
            rel_from_pleb = pleb.solutions.connect(self)
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
            edit_solution = Solution(object_uuid=str(uuid1()), original=False,
                                       content=content).save()
            self.edits.connect(edit_solution)
            edit_solution.edit_to.connect(self)
            self.last_edited_on = datetime.now(pytz.utc)
            self.save()
            return edit_solution
        except CypherException as e:
            return e