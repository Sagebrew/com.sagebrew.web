from rest_framework import serializers


class PublicOfficialSerializer(serializers.Serializer):
    object_uuid = serializers.CharField()
    full_name = serializers.CharField()
    start_date = serializers.DateTimeField(read_only=True)
    end_date = serializers.DateTimeField(read_only=True)
    state = serializers.CharField(read_only=True)
    district = serializers.IntegerField(read_only=True)
    current = serializers.BooleanField(read_only=True)
