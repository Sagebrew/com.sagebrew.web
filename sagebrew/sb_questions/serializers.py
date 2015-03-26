from rest_framework import serializers


class QuestionSerializerNeo(serializers.Serializer):
    object_uuid = serializers.CharField(read_only=True)
    href = serializers.HyperlinkedIdentityField(view_name='question-detail',
                                                lookup_field="object_uuid")
    content = serializers.CharField()

    last_edited_on = serializers.DateTimeField(read_only=True)
    upvotes = serializers.CharField(read_only=True)
    downvotes = serializers.CharField(read_only=True)

    def create(self, validated_data):
        # TODO should store in dynamo and then spawn task to store in Neo
        pass

    def update(self, instance, validated_data):
        # TODO get from dynamo and then spawn task to store in Neo
        pass
