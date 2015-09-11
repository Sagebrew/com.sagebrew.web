import bleach
import pytz
from datetime import datetime

from django.conf import settings
from django.core.cache import cache

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import db, DoesNotExist

from api.utils import spawn_task, gather_request_data
from sb_base.serializers import TitledContentSerializer
from plebs.neo_models import Pleb
from sb_tags.neo_models import Tag
from sb_tags.tasks import update_tags
from sb_solutions.serializers import SolutionSerializerNeo
from sb_solutions.neo_models import Solution

from .neo_models import Question
from .tasks import add_auto_tags_to_question_task, update_search_index


def solution_count(question_uuid):
    query = 'MATCH (a:Question {object_uuid: "%s"})-' \
            '[:POSSIBLE_ANSWER]->(solutions:Solution) ' \
            'WHERE solutions.to_be_deleted = false ' \
            'RETURN count(DISTINCT solutions)' % question_uuid
    res, col = db.cypher_query(query)
    try:
        count = res[0][0]
    except IndexError:
        count = 0
    return count


class QuestionTitleUpdate:
    """
    This class will attempt to get the parent instance of the serializer and
    set self.object_uuid to it, this allows it to validate that there are no
    solutions to a question when attempting to update the tile of a question,
    but also allows creation of the question by setting self.object_uuid to
    None if there is not an instance in the serializer.
    """
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
        if self.object_uuid is not None:
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


class QuestionSerializerNeo(TitledContentSerializer):
    content = serializers.CharField(min_length=15)
    href = serializers.SerializerMethodField()
    # This might be better as a choice field
    tags = serializers.ListField(
        source='get_tags',
        validators=[limit_5_tags, PopulateTags()],
        child=serializers.CharField(max_length=36),
    )
    title = serializers.CharField(required=False,
                                  validators=[QuestionTitleUpdate(), ],
                                  min_length=15, max_length=140)
    solutions = serializers.SerializerMethodField()
    solution_count = serializers.SerializerMethodField()

    def create(self, validated_data):
        request = self.context["request"]
        # Note that DRF requires us to use the source as the key here but
        # tags prior to serializing
        tags = validated_data.pop('get_tags', [])
        owner = Pleb.get(request.user.username)
        validated_data['content'] = bleach.clean(validated_data.get(
            'content', ""))
        validated_data['owner_username'] = owner.username
        question = Question(**validated_data).save()
        question.owned_by.connect(owner)
        owner.questions.connect(question)
        for tag in tags:
            try:
                tag_obj = Tag.nodes.get(name=tag.lower())
            except(Tag.DoesNotExist, DoesNotExist):
                if settings.DEBUG is True:
                    # TODO this is only here because we don't have a stable
                    # setup for ES and initial tags. Once @matt finishes up
                    # ansible and we can get tags to register consistently
                    # we can remove this.
                    if (request.user.username == "devon_bleibtrey" or
                            request.user.username == "tyler_wiersing"):
                        tag_obj = Tag(name=tag.lower()).save()
                    else:
                        continue
                else:
                    continue
            question.tags.connect(tag_obj)
        spawn_task(task_func=update_tags, task_param={"tags": tags})
        spawn_task(task_func=add_auto_tags_to_question_task, task_param={
            "object_uuid": question.object_uuid})
        question.refresh()
        cache.set(question.object_uuid, question)
        return question

    def update(self, instance, validated_data):
        # TODO do we want to allow for tags to be changed?
        # I don't think we do because of the tight coupling with Reputation
        # and search. I think it could be exploited too easily.
        """
        When we start doing versioning:
        edit = Question(title=validated_data.get('title', instance.title),
                        content=validated_data.get('content', instance.content))
        edit.save()
        instance.edits.connect(edit)
        edit.edit_to.connect(instance)
        """
        instance.title = validated_data.get('title', instance.title)
        instance.content = bleach.clean(validated_data.get('content',
                                                           instance.content))
        instance.last_edited_on = datetime.now(pytz.utc)
        instance.save()
        cache.delete(instance.object_uuid)
        spawn_task(task_func=add_auto_tags_to_question_task, task_param={
            "object_uuid": instance.object_uuid})
        spawn_task(task_func=update_search_index, task_param={
            "object_uuid": instance.object_uuid})
        return instance

    def get_url(self, obj):
        return obj.get_url(request=self.context.get('request', None))

    def get_solution_count(self, obj):
        return solution_count(obj.object_uuid)

    def get_solutions(self, obj):
        request, expand, _, relations, expedite = gather_request_data(
            self.context,
            expedite_param=self.context.get('expedite_param', None),
            expand_param=self.context.get('expand_param', None))
        if expedite == "true":
            return []
        solutions = obj.get_solution_ids()
        solution_urls = []
        if expand == "true":
            for solution_uuid in solutions:
                query = 'MATCH (s:Solution {object_uuid: "%s"}) RETURN s' % (
                    solution_uuid)
                res, _ = db.cypher_query(query)
                solution_urls.append(SolutionSerializerNeo(
                    Solution.inflate(res.one),
                    context={"request": request,
                             "expand_param": self.context.get('expand_param',
                                                              None)}).data)
        else:
            if relations == "hyperlinked":
                for solution_uuid in solutions:
                    solution_urls.append(reverse(
                        'solution-detail', kwargs={
                            'object_uuid': solution_uuid},
                        request=request))
            else:
                return solutions

        return solution_urls

    def get_href(self, obj):
        request, _, _, _, _ = gather_request_data(
            self.context,
            expedite_param=self.context.get('expedite_param', None),
            expand_param=self.context.get('expand_param', None))
        return reverse(
            'question-detail', kwargs={'object_uuid': obj.object_uuid},
            request=request)
