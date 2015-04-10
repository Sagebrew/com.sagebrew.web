from rest_framework import serializers
from rest_framework.reverse import reverse

from sb_base.serializers import MarkdownContentSerializer


class QuestionSerializerNeo(MarkdownContentSerializer):
    href = serializers.HyperlinkedIdentityField(view_name='question-detail',
                                                lookup_field="object_uuid")
    title = serializers.CharField(required=False)
    solution_count = serializers.IntegerField(read_only=True)

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