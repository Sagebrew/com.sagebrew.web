from rest_framework import serializers


class SBSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.object_uuid

    def get_type(self, obj):
        return obj.__class__.__name__.lower()