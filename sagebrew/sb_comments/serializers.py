from rest_framework import serializers

from .neo_models import SBComment


class CommentSerializer(serializers.Serializer):
    object_uuid = serializers.CharField(read_only=True)
    parent_object = serializers.CharField(read_only=True)
    content = serializers.CharField()
    # TODO add owner pleb and utilize def perform_create(self, serializer)
    # to store off owner of comment

    def create(self, validated_data):
        comment = SBComment(**validated_data).save()
        return comment

    def update(self, instance, validated_data):
        # TODO get from dynamo and then spawn task to store in Neo
        pass