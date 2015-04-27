from rest_framework import serializers

from api.serializers import SBSerializer


class PublicOfficialSerializer(SBSerializer):
    object_uuid = serializers.CharField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    bioguide = serializers.CharField(read_only=True)
    youtube = serializers.CharField(read_only=True)
    twitter = serializers.CharField(read_only=True)
    channel_wallpaper = serializers.CharField(read_only=True)
    start_date = serializers.DateTimeField(read_only=True)
    end_date = serializers.DateTimeField(read_only=True)
    state = serializers.CharField(read_only=True)
    district = serializers.IntegerField(read_only=True)
    current = serializers.BooleanField(read_only=True)

    def get_type(self, obj):
        return "public_official"
