import bleach
import pytz
from uuid import uuid1
from datetime import datetime

from django.core.cache import cache
from django.utils.text import slugify

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import db

from api.utils import spawn_task, gather_request_data, smart_truncate
from sb_base.serializers import TitledContentSerializer
from plebs.neo_models import Pleb
from sb_locations.tasks import create_location_tree

from sb_tags.neo_models import Tag
from sb_tags.tasks import update_tags
from sb_solutions.serializers import SolutionSerializerNeo
from sb_solutions.neo_models import Solution

from .neo_models import Question
from .tasks import (add_auto_tags_to_question_task,
                    create_question_summary_task)


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
    summary = serializers.CharField(read_only=True)
    # This might be better as a choice field
    tags = serializers.ListField(
        source='get_tags',
        validators=[limit_5_tags, PopulateTags()],
        child=serializers.CharField(max_length=240),
    )
    title = serializers.CharField(required=False,
                                  validators=[QuestionTitleUpdate(), ],
                                  min_length=15, max_length=140)
    solutions = serializers.SerializerMethodField()
    solution_count = serializers.SerializerMethodField()
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    affected_area = serializers.CharField(required=False, allow_null=True)
    # Used to associate Question with our tree structure after tasks have
    # been completed and Question has been created
    external_location_id = serializers.CharField(write_only=True,
                                                 required=False,
                                                 allow_null=True)
    tags_formatted = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()
    mission = serializers.SerializerMethodField()

    def validate_title(self, value):
        # We need to escape quotes prior to passing the title to the query.
        # Otherwise the query will fail due to the string being terminated.
        if self.instance is not None and self.instance.title == value:
            return value
        temp_value = value
        temp_value = temp_value.replace('"', '\\"')
        temp_value = temp_value.replace("'", "\\'")
        query = 'MATCH (q:Question {title: "%s"}) RETURN q' % temp_value
        res, _ = db.cypher_query(query)
        if res.one is not None:
            raise serializers.ValidationError("Sorry looks like a Question "
                                              "with that Title already exists.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        # Note that DRF requires us to use the source as the key here but
        # tags prior to serializing
        tags = validated_data.pop('get_tags', [])
        owner = Pleb.get(request.user.username)
        validated_data['content'] = bleach.clean(validated_data.get(
            'content', ""))
        validated_data['owner_username'] = owner.username
        uuid = str(uuid1())
        url = reverse('question_detail_page', kwargs={'question_uuid': uuid,
                                                      "slug": slugify(
                                                          validated_data[
                                                              'title'])},
                      request=request)
        href = reverse('question-detail', kwargs={'object_uuid': uuid},
                       request=request)

        question = Question(url=url, href=href, object_uuid=uuid,
                            summary=smart_truncate(validated_data['content']),
                            **validated_data).save()
        question.owned_by.connect(owner)
        for tag in tags:
            query = 'MATCH (t:Tag {name:"%s"}) WHERE NOT t:AutoTag ' \
                    'RETURN t' % slugify(tag)
            res, _ = db.cypher_query(query)
            if not res.one:
                if (request.user.username == "devon_bleibtrey" or
                        request.user.username == "tyler_wiersing" or
                        owner.reputation > 1250):
                    tag_obj = Tag(name=slugify(tag)).save()
                    question.tags.connect(tag_obj)
                else:
                    continue
            else:
                tag_obj = Tag.inflate(res.one)
                question.tags.connect(tag_obj)
        spawn_task(task_func=update_tags, task_param={"tags": tags})
        if validated_data.get('external_location_id', None) is not None:
            spawn_task(task_func=create_location_tree, task_param={
                "external_id": question.external_location_id})
        spawn_task(task_func=add_auto_tags_to_question_task, task_param={
            "object_uuid": question.object_uuid})
        spawn_task(task_func=create_question_summary_task, task_param={
            'object_uuid': question.object_uuid
        })
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
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get(
            'longitude', instance.longitude)
        instance.affected_area = validated_data.get('affected_area',
                                                    instance.affected_area)
        instance.external_location_id = validated_data.get(
            'external_location_id', instance.external_location_id)
        instance.save()
        cache.delete(instance.object_uuid)
        if validated_data.get('external_location_id', None) is not None:
            spawn_task(task_func=create_location_tree, task_param={
                "external_id": instance.external_location_id})
        spawn_task(task_func=add_auto_tags_to_question_task, task_param={
            "object_uuid": instance.object_uuid})
        spawn_task(task_func=create_question_summary_task, task_param={
            'object_uuid': instance.object_uuid
        })
        return super(QuestionSerializerNeo, self).update(
            instance, validated_data)

    def get_url(self, obj):
        return obj.get_url(request=self.context.get('request', None))

    def get_solution_count(self, obj):
        return solution_count(obj.object_uuid)

    def get_solutions(self, obj):
        expand_param = self.context.get('expand_param', None)
        request, expand, _, relations, expedite = gather_request_data(
            self.context,
            expedite_param=self.context.get('expedite_param', None),
            expand_param=expand_param)
        if expedite == "true":
            return []
        solutions = []
        if expand == "true" and relations != "hyperlink":
            query = 'MATCH (a:Question {object_uuid: "%s"})' \
                '-[:POSSIBLE_ANSWER]->(solutions:Solution) ' \
                'WHERE solutions.to_be_deleted = false ' \
                'RETURN solutions' % obj.object_uuid
            res, _ = db.cypher_query(query)
            solutions = SolutionSerializerNeo(
                [Solution.inflate(row[0]) for row in res], many=True,
                context={"request": request, "expand_param": expand_param}).data
        else:
            if relations == "hyperlink":
                solutions = [
                    reverse('solution-detail',
                            kwargs={'object_uuid': solution_uuid},
                            request=request)
                    for solution_uuid in obj.get_solution_ids()
                ]
            else:
                return solutions

        return solutions

    def get_href(self, obj):
        request, _, _, _, _ = gather_request_data(
            self.context,
            expedite_param=self.context.get('expedite_param', None),
            expand_param=self.context.get('expand_param', None))
        return reverse(
            'question-detail', kwargs={'object_uuid': obj.object_uuid},
            request=request)

    def get_tags_formatted(self, obj):
        return ", ".join([tag.replace("-", " ").replace("_", " ").title()
                         for tag in obj.get_tags()])

    def get_mission(self, obj):
        from sb_missions.serializers import MissionSerializer
        query = 'MATCH (question:Question)<-[:ASSOCIATED_WITH]-' \
                '(mission:Mission) RETURN mission'
        res, _ = db.cypher_query(query)
        if res.one:
            return MissionSerializer(res.one).data
        return res.one

    def get_views(self, obj):
        return obj.get_view_count()
