from rest_framework import serializers

from api.serializers import SBSerializer


class PublicOfficialSerializer(SBSerializer):
    object_uuid = serializers.CharField()
    role_id = serializers.CharField()
    full_name = serializers.CharField()
    start_date = serializers.DateTimeField(read_only=True)
    end_date = serializers.DateTimeField(read_only=True)
    state = serializers.CharField(read_only=True)
    district = serializers.IntegerField(read_only=True)
    current = serializers.BooleanField(read_only=True)

    def get_type(self, obj):
        return "public_official"
