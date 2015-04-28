from localflavor.us.us_states import US_STATES

from rest_framework import serializers

from api.serializers import SBSerializer


class PublicOfficialSerializer(SBSerializer):
    object_uuid = serializers.CharField(read_only=True)
    full_name = serializers.SerializerMethodField()
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    title = serializers.SerializerMethodField()
    bioguideid = serializers.CharField(read_only=True)
    youtube = serializers.CharField(read_only=True)
    twitter = serializers.CharField(read_only=True)
    channel_wallpaper = serializers.SerializerMethodField()
    start_date = serializers.DateTimeField(read_only=True)
    end_date = serializers.DateTimeField(read_only=True)
    state = serializers.SerializerMethodField()
    district = serializers.IntegerField(read_only=True)
    current = serializers.BooleanField(read_only=True)
    terms = serializers.SerializerMethodField()

    def get_type(self, obj):
        return "public_official"

    def get_state(self, obj):
        try:
            return dict(US_STATES)[obj.state]
        except KeyError:
            return obj.state

    def get_full_name(self, obj):
        try:
            crop_name = str(obj.full_name).rfind('[')
        except UnicodeEncodeError:
            return obj.full_name
        try:
            full_name = obj.full_name[:crop_name]
        except IndexError:
            full_name = obj.full_name
        return full_name

    def get_terms(self, obj):
        return obj.terms

    def get_title(self, obj):
        if obj.title == "Sen.":
            return "Senator"
        elif obj.title == "Rep.":
            return "House Representative"
        else:
            return obj.title

    def get_channel_wallpaper(self, obj):
        return None
