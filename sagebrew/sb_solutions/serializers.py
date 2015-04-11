from rest_framework import serializers
from rest_framework.reverse import reverse

from sb_base.serializers import MarkdownContentSerializer

from .neo_models import Solution


class SolutionSerializerNeo(MarkdownContentSerializer):
    href = serializers.HyperlinkedIdentityField(view_name='solution-detail',
                                                lookup_field="object_uuid")
    solution_to = serializers.SerializerMethodField()

    def create(self, validated_data):
        # TODO should store in dynamo and then spawn task to store in Neo
        solution = Solution(**validated_data).save()
        return solution

    def update(self, instance, validated_data):
        # TODO get from dynamo and then spawn task to store in Neo
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