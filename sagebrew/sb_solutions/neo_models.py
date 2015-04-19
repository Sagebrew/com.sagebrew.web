from neomodel import (RelationshipTo)

from sb_base.neo_models import SBPublicContent


class Solution(SBPublicContent):
    table = 'public_solutions'
    action_name = "offered a solution to a question"
    up_vote_adjustment = 10
    down_vote_adjustment = 10
    down_vote_cost = 2

    # relationships
    solution_to = RelationshipTo('sb_questions.neo_models.Question',
                                 'POSSIBLE_ANSWER_TO')
