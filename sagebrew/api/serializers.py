from rest_framework import serializers


class SBSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    def get_id(self, obj):
        request = self.context.get('request')
        # TODO may want to change this to async?
        try:
            expedite = request.query_params.get('expedite', "false").lower()
        except AttributeError:
            try:
                expedite = request.GET.get('expedite', "false").lower()
            except AttributeError:
                return None
        if expedite == "true":
            return None
        return obj.object_uuid

    def get_type(self, obj):
        request = self.context.get('request')
        # TODO may want to change this to async?
        try:
            expedite = request.query_params.get('expedite', "false").lower()
        except AttributeError:
            try:
                expedite = request.GET.get('expedite', "false").lower()
            except AttributeError:
                return None
        if expedite == "true":
            return None
        return obj.__class__.__name__.lower()
