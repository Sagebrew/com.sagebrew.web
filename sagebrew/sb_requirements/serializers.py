from rest_framework import serializers

from api.serializers import SBSerializer


class RequirementSerializer(SBSerializer):
    name = serializers.CharField()
    url = serializers.URLField()
    key = serializers.CharField()
    operator = serializers.CharField()
    condition = serializers.CharField()
    auth_type = serializers.CharField()