from rest_framework import serializers


class SBSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    def get_id(self, obj):
        try:
            request = self.context['request']
            try:
                # TODO may want to change this to async?
                expedite = request.query_params.get('expedite', "false").lower()
            except AttributeError:
                try:
                    expedite = request.GET.get('expedite', "false").lower()
                except AttributeError:
                    return None
            if expedite == "true":
                return None
        except KeyError:
            pass

        return obj.object_uuid

    def get_type(self, obj):
        try:
            request = self.context['request']
            try:
                # TODO may want to change this to async?
                expedite = request.query_params.get('expedite', "false").lower()
            except AttributeError:
                try:
                    expedite = request.GET.get('expedite', "false").lower()
                except AttributeError:
                    return None
            if expedite == "true":
                return None
        except KeyError:
            pass

        return obj.__class__.__name__.lower()
