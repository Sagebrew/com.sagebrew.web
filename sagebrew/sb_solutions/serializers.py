from rest_framework import serializers
from rest_framework.reverse import reverse

from sb_base.serializers import MarkdownContentSerializer
from plebs.neo_models import Pleb
from sb_questions.neo_models import Question

from .neo_models import Solution


class SolutionSerializerNeo(MarkdownContentSerializer):
    href = serializers.HyperlinkedIdentityField(view_name='solution-detail',
                                                lookup_field="object_uuid")
    solution_to = serializers.SerializerMethodField()

    def create(self, validated_data):
        request = self.context["request"]
        question_uuid = validated_data.pop('question', None)
        owner = Pleb.nodes.get(username=request.user.username)
        question = Question.nodes.get(object_uuid=question_uuid)
        solution = Solution(**validated_data).save()
        solution.owned_by.connect(owner)
        owner.solutions.connect(solution)
        question.solutions.connect(solution)

        return solution

    def update(self, instance, validated_data):
        pass

    def get_url(self, obj):
        question = obj.solution_to.all()[0]
        return reverse('question_detail_page',
                       kwargs={'question_uuid': question.object_uuid},
                       request=self.context['request'])

    def get_solution_to(self, obj):
        question = obj.solution_to.all()[0]
        return reverse('question-detail',
                       kwargs={'object_uuid': question.object_uuid},
                       request=self.context['request'])