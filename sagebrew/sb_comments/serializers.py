from rest_framework import serializers


class CommentSerializer(serializers.Serializer):
    object_uuid = serializers.CharField()
    parent_object = serializers.CharField()
    content = serializers.CharField()

    def create(self, validated_data):
        # TODO should store in dynamo and then spawn task to store in Neo
        pass

    def update(self, instance, validated_data):
        # TODO get from dynamo and then spawn task to store in Neo
        pass