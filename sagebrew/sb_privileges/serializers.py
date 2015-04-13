from rest_framework import serializers


class ActionSerializer(serializers.Serializer):
    resource = serializers.CharField()
    permission = serializers.CharField()
    url = serializers.URLField()