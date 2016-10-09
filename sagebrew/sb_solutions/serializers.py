import pytz
from bs4 import BeautifulSoup

from uuid import uuid1
from datetime import datetime

from rest_framework import serializers
from rest_framework.reverse import reverse

from api.utils import (gather_request_data, spawn_task, smart_truncate,
                       render_content)
from sb_base.serializers import ContentSerializer, validate_is_owner
from plebs.neo_models import Pleb
from .tasks import create_solution_summary_task
from .neo_models import Solution


class SolutionSerializerNeo(ContentSerializer):
    content = serializers.CharField(min_length=15)
    href = serializers.HyperlinkedIdentityField(view_name='solution-detail',
                                                lookup_field="object_uuid")
    parent_id = serializers.CharField(read_only=True)
    question = serializers.SerializerMethodField()
    mission = serializers.SerializerMethodField()
    summary = serializers.CharField(read_only=True)

    def create(self, validated_data):
        request = self.context["request"]
        question = validated_data.pop('question', None)
        owner = Pleb.get(request.user.username)
        validated_data['owner_username'] = owner.username
        uuid = str(uuid1())
        validated_data['content'] = render_content(
            validated_data.get('content', ""))
        href = reverse('solution-detail', kwargs={"object_uuid": uuid},
                       request=request)
        soup = BeautifulSoup(validated_data['content'], "lxml").get_text()
        solution = Solution(url=question.url, href=href, object_uuid=uuid,
                            parent_id=question.object_uuid,
                            summary=smart_truncate(soup),
                            **validated_data).save()
        solution.owned_by.connect(owner)
        question.solutions.connect(solution)
        spawn_task(task_func=create_solution_summary_task, task_param={
            'object_uuid': solution.object_uuid
        })
        return solution

    def update(self, instance, validated_data):
        validate_is_owner(self.context.get('request', None), instance)
        instance.content = render_content(
            validated_data.get('content', instance.content))
        instance.last_edited_on = datetime.now(pytz.utc)
        instance.save()
        spawn_task(task_func=create_solution_summary_task, task_param={
            'object_uuid': instance.object_uuid
        })
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

    def get_mission(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return obj.get_mission(obj.object_uuid, request)
