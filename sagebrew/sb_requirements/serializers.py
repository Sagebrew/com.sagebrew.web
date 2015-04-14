from rest_framework import serializers


class RequirementSerializer(serializers.Serializer):
    name = serializers.CharField()
    url = serializers.URLField()
    key = serializers.CharField()
    operator = serializers.CharField()
    condition = serializers.CharField()
    auth_type = serializers.CharField()