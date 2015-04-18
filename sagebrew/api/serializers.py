from rest_framework import serializers


class SBSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    def get_id(self, obj):
        request = self.context.get('request')
        # TODO may want to change this to async?
        expedite = request.query_params.get('expedite', "false").lower()
        if expedite == "true":
            return None
        return obj.object_uuid

    def get_type(self, obj):
        request = self.context.get('request')
        # TODO may want to change this to async?
        expedite = request.query_params.get('expedite', "false").lower()
        if expedite == "true":
            return None
        return obj.__class__.__name__.lower()