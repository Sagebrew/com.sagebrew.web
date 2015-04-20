from rest_framework import serializers

from api.serializers import SBSerializer

from .neo_models import Badge


class BadgeSerializer(SBSerializer):
    object_uuid = serializers.CharField(read_only=True)
    name = serializers.CharField()
    image_color = serializers.CharField()
    image_grey = serializers.CharField()

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Badge(**validated_data).save()

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the
        validated data.
        """
        instance.name = validated_data.get('title', instance.title)
        instance.image_color = validated_data.get('code', instance.code)
        instance.image_grey = validated_data.get('linenos', instance.linenos)
        instance.save()
        return instance
