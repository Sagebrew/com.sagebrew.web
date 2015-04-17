import pytz
from datetime import datetime

from django.conf import settings

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import db, DoesNotExist

from api.utils import spawn_task
from sb_base.serializers import MarkdownContentSerializer
from plebs.neo_models import Pleb
from sb_tag.neo_models import Tag
from sb_tag.tasks import update_tags

from .neo_models import Question
from .tasks import add_auto_tags_to_question_task


def solution_count(question_uuid):
    query = 'MATCH (a:Question)-->(solutions:Solution) ' \
            'WHERE (a.object_uuid = "%s" and ' \
            'solutions.to_be_deleted = false)' \
            'RETURN count(DISTINCT solutions)' % (question_uuid)
    res, col = db.cypher_query(query)
    try:
        count = res[0][0]
    except IndexError:
        count = 0
    return count


class TitleUpdate:
    def __init__(self):
        pass

    def __call__(self, value):
        if (self.object_uuid is not None and
                    solution_count(self.object_uuid) > 0):
            message = 'Cannot edit Title when there have ' \
                      'already been solutions provided'
            raise serializers.ValidationError(message)
        return value

    def set_context(self, serializer_field):
        try:
            self.object_uuid = serializer_field.parent.instance.object_uuid
        except AttributeError:
            self.object_uuid = None


class PopulateTags:
    def __init__(self):
        pass

    def __call__(self, value):
        if (self.object_uuid is not None):
            message = 'Sorry you cannot add or change tags after the ' \
                      'creation of a Question. We tie Reputation and' \
                      " search tightly to these values and don't want " \
                      "to confuse users with changes to them."
            raise serializers.ValidationError(message)
        return value

    def set_context(self, serializer_field):
        try:
            self.object_uuid = serializer_field.parent.instance.object_uuid
        except AttributeError:
            self.object_uuid = None


def limit_5_tags(value):
    # TODO could potentially set the hard coded 5 based on the rank of the
    # user
    if len(value) > 5:
        raise serializers.ValidationError('Only allow up to 5 tags')
    return value


# TODO create a validator that only enables people of a certain rank to
# create new tags, right now it's open season


class QuestionSerializerNeo(MarkdownContentSerializer):
    content = serializers.CharField(min_length=15)
    href = serializers.HyperlinkedIdentityField(view_name='question-detail',
                                                lookup_field="object_uuid")
    title = serializers.CharField(required=False,
                                  validators=[TitleUpdate(), ],
                                  min_length=15, max_length=140)
    # This might be better as a choice field
    tags = serializers.ListField(
        source='get_tags',
        validators=[limit_5_tags, PopulateTags()],
        child=serializers.CharField(max_length=36),
    )

    solution_count = serializers.SerializerMethodField()

    def create(self, validated_data):
        request = self.context["request"]
        # Note that DRF requires us to use the source as the key here but
        # tags prior to serializing
        tags = validated_data.pop('get_tags', [])
        owner = Pleb.nodes.get(username=request.user.username)
        question = Question(**validated_data).save()
        question.owned_by.connect(owner)
        owner.questions.connect(question)
        for tag in tags:
            try:
                tag_obj = Tag.nodes.get(name=tag)
            except(Tag.DoesNotExist, DoesNotExist):
                if settings.DEBUG is True:
                    # TODO this is only here because we don't have a stable
                    # setup for ES and initial tags. Once @matt finishes up
                    # ansible and we can get tags to register consistently
                    # we can remove this.
                    if (request.user.username == "devon_bleibtrey" or
                                request.user.username == "tyler_wiersing"):
                        tag_obj = Tag(name=tag).save()
                    else:
                        continue
                else:
                    continue
            question.tags.connect(tag_obj)
        spawn_task(task_func=update_tags, task_param={"tags": tags})
        spawn_task(task_func=add_auto_tags_to_question_task, task_param={
            "object_uuid": question.object_uuid})
        return question

    def update(self, instance, validated_data):
        # TODO do we want to allow for tags to be changed?
        # I don't think we do because of the tight coupling with Reputation
        # and search. I think it could be exploited too easily.
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.last_edited_on = datetime.now(pytz.utc)
        instance.save()
        spawn_task(task_func=add_auto_tags_to_question_task, task_param={
            "object_uuid": instance.object_uuid})

        return instance

    def get_url(self, obj):
        return reverse('question_detail_page',
                       kwargs={'question_uuid': obj.object_uuid},
                       request=self.context['request'])

    def get_solution_count(self, obj):
        return solution_count(obj.object_uuid)
