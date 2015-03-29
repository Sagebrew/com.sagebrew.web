from rest_framework import serializers

from .neo_models import SBComment


class CommentSerializer(serializers.Serializer):
    object_uuid = serializers.CharField(read_only=True)
    object_type = serializers.CharField(read_only=True)
    parent_object = serializers.CharField(read_only=True)
    content = serializers.CharField()
    owner = serializers.CharField(read_only=True)
    owner_full_name = serializers.CharField(read_only=True)
    last_edited_on = serializers.DateTimeField()
    created = serializers.DateTimeField(read_only=True)
    vote_count = serializers.CharField()
    upvotes = serializers.IntegerField()
    downvotes = serializers.IntegerField()

    # TODO add owner pleb and utilize def perform_create(self, serializer)
    # to store off owner of comment

    def create(self, validated_data):
        comment = SBComment(**validated_data).save()
        return comment

    def update(self, instance, validated_data):
        # TODO get from dynamo and then spawn task to store in Neo
        pass