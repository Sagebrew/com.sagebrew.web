from rest_framework.reverse import reverse

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

    def get_url(self, request=None):
        question = self.solution_to.all()[0]
        return reverse('question_detail_page',
                       kwargs={'question_uuid': question.object_uuid},
                       request=request)
