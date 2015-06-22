from rest_framework import serializers


class SBSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    def get_id(self, obj):
        try:
            return obj.object_uuid
        except AttributeError:
            return None

    def get_type(self, obj):
        try:
            return obj.__class__.__name__.lower()
        except AttributeError:
            return None

