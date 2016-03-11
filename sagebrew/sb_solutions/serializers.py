import bleach
import pytz

from uuid import uuid1
from datetime import datetime

from rest_framework import serializers
from rest_framework.reverse import reverse

from api.utils import gather_request_data
from sb_base.serializers import MarkdownContentSerializer
from plebs.neo_models import Pleb


from .neo_models import Solution


class SolutionSerializerNeo(MarkdownContentSerializer):
    content = serializers.CharField(min_length=15)
    href = serializers.HyperlinkedIdentityField(view_name='solution-detail',
                                                lookup_field="object_uuid")
    parent_id = serializers.CharField(read_only=True)
    question = serializers.SerializerMethodField()

    def create(self, validated_data):
        request = self.context["request"]
        question = validated_data.pop('question', None)
        owner = Pleb.get(request.user.username)
        validated_data['content'] = bleach.clean(validated_data.get(
            'content', ""))
        validated_data['owner_username'] = owner.username
        uuid = str(uuid1())
        href = reverse('solution-detail', kwargs={"object_uuid": uuid},
                       request=request)
        solution = Solution(url=question.url, href=href, object_uuid=uuid,
                            parent_id=question.object_uuid,
                            **validated_data).save()
        solution.owned_by.connect(owner)
        owner.solutions.connect(solution)
        question.solutions.connect(solution)

        return solution

    def update(self, instance, validated_data):
        instance.content = bleach.clean(validated_data.get('content',
                                                           instance.content))
        instance.last_edited_on = datetime.now(pytz.utc)
        instance.save()

        return instance

    def get_url(self, obj):
        return obj.get_url(self.context.get('request', None))

    def get_question(self, obj):
        from sb_questions.neo_models import Question
        from sb_questions.serializers import QuestionSerializerNeo
        request, expand, _, relations, expedite = gather_request_data(
            self.context,
            expedite_param=self.context.get('expedite_param', None),
            expand_param=self.context.get('expand_param', None))
        question = Question.get(object_uuid=obj.parent_id)
        if expand:
            return QuestionSerializerNeo(question).data
        return reverse('question-detail',
                       kwargs={'object_uuid': question.object_uuid},
                       request=self.context.get('request', None))
