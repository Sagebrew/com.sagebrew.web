from rest_framework.reverse import reverse

from neomodel import (RelationshipTo, StringProperty, IntegerProperty)

from sb_base.neo_models import SBPublicContent


class Solution(SBPublicContent):
    table = StringProperty(default='public_solutions')
    action_name = StringProperty(default="offered a solution to your question")
    visibility = StringProperty(default="public")
    up_vote_adjustment = IntegerProperty(default=10)
    down_vote_adjustment = IntegerProperty(default=-10)
    down_vote_cost = IntegerProperty(default=-2)

    # relationships
    solution_to = RelationshipTo('sb_questions.neo_models.Question',
                                 'POSSIBLE_ANSWER_TO')

    def get_url(self, request=None):
        question = self.solution_to.all()[0]
        return reverse('question_detail_page',
                       kwargs={'question_uuid': question.object_uuid},
                       request=request)
