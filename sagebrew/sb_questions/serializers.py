from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import db

from sb_base.serializers import MarkdownContentSerializer


class QuestionSerializerNeo(MarkdownContentSerializer):
    href = serializers.HyperlinkedIdentityField(view_name='question-detail',
                                                lookup_field="object_uuid")
    title = serializers.CharField(required=False)
    # TODO change this to method
    solution_count = serializers.SerializerMethodField(read_only=True)

    def create(self, validated_data):
        # TODO should store in dynamo and then spawn task to store in Neo
        pass

    def update(self, instance, validated_data):
        # TODO get from dynamo and then spawn task to store in Neo
        pass

    def get_url(self, obj):
        return reverse('question_detail_page',
                       kwargs={'question_uuid': obj.object_uuid},
                       request=self.context['request'])

    def get_solution_count(self, obj):
        return solution_count(obj.object_uuid)

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