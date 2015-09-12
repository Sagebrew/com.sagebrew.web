import bleach
import pytz

from uuid import uuid1
from datetime import datetime

from rest_framework import serializers
from rest_framework.reverse import reverse

from sb_base.serializers import MarkdownContentSerializer
from plebs.neo_models import Pleb


from .neo_models import Solution


class SolutionSerializerNeo(MarkdownContentSerializer):
    href = serializers.HyperlinkedIdentityField(view_name='solution-detail',
                                                lookup_field="object_uuid")
    solution_to = serializers.SerializerMethodField()

    def create(self, validated_data):
        request = self.context["request"]
        question = validated_data.pop('question', None)
        owner = Pleb.get(request.user.username)
        validated_data['content'] = bleach.clean(validated_data.get(
            'content', ""))
        validated_data['owner_username'] = owner.username
        uuid = str(uuid1())
        url = reverse('question_detail_page',
                      kwargs={'question_uuid': question.object_uuid},
                      request=request)
        href = reverse('solution-detail', kwargs={"object_uuid": uuid},
                       request=request)
        solution = Solution(url=url, href=href, object_uuid=uuid,
                            **validated_data).save()
        solution.owned_by.connect(owner)
        owner.solutions.connect(solution)
        if question is not None:
            question.solutions.connect(solution)
            solution.solution_to.connect(question)

        return solution

    def update(self, instance, validated_data):
        instance.content = bleach.clean(validated_data.get('content',
                                                           instance.content))
        instance.last_edited_on = datetime.now(pytz.utc)
        instance.save()

        return instance

    def get_url(self, obj):
        return obj.get_url(self.context.get('request', None))

    def get_solution_to(self, obj):
        try:
            question = obj.solution_to.all()[0]
        except IndexError:
            return None
        return reverse('question-detail',
                       kwargs={'object_uuid': question.object_uuid},
                       request=self.context.get('request', None))
