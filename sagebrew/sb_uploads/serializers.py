from rest_framework.reverse import reverse
from rest_framework import serializers
from neomodel import db

from api.utils import request_to_api, gather_request_data
from api.serializers import SBSerializer
from sb_base.neo_models import SBContent


class MediaType:
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


class UploadSerializer(SBSerializer):
    media_type = serializers.CharField()
    url = serializers.SerializerMethodField()
    vote_on = serializers.SerializerMethodField()

    def create(self, validated_data):
        return None

    def update(self, instance, validated_data):
        return None
