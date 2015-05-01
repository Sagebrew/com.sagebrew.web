from rest_framework import serializers

from api.serializers import SBSerializer


class MediaType:
    def __init__(self):
        pass

    def __call__(self, value):
        if (self.media_type not in ['']):
            message = 'Cannot edit Title when there have ' \
                      'already been solutions provided'
            raise serializers.ValidationError(message)
        return value

    def set_context(self, serializer_field):
        try:
            self.media_type = serializer_field.parent.instance.media_type
        except AttributeError:
            self.media_type = None


class UploadSerializer(SBSerializer):
    media_type = serializers.CharField()
    url = serializers.SerializerMethodField()
    vote_on = serializers.SerializerMethodField()

    def create(self, validated_data):
        return None

    def update(self, instance, validated_data):
        return None
