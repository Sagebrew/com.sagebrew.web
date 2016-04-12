from django.utils.text import slugify
from rest_framework.reverse import reverse

from neomodel import (StringProperty, IntegerProperty)

from sb_base.neo_models import SBPublicContent


class Solution(SBPublicContent):
    table = StringProperty(default='public_solutions')
    action_name = StringProperty(default="offered a solution to your question")
    parent_id = StringProperty()
    visibility = StringProperty(default="public")
    up_vote_adjustment = IntegerProperty(default=10)
    down_vote_adjustment = IntegerProperty(default=-10)
    down_vote_cost = IntegerProperty(default=-2)

    def get_url(self, request=None):
        from sb_questions.neo_models import Question
        question = Question.get(object_uuid=self.parent_id)
        return reverse('question_detail_page',
                       kwargs={'question_uuid': self.parent_id,
                               'slug': slugify(question.title)},
                       request=request)
