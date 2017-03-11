from localflavor.us.us_states import US_STATES

from rest_framework import serializers

from neomodel import db

from sagebrew.api.serializers import SBSerializer


class PublicOfficialSerializer(SBSerializer):
    object_uuid = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    bioguideid = serializers.CharField(read_only=True)
    youtube = serializers.CharField(read_only=True)
    twitter = serializers.CharField(read_only=True)
    start_date = serializers.DateTimeField(read_only=True)
    end_date = serializers.DateTimeField(read_only=True)
    district = serializers.IntegerField(read_only=True)
    current = serializers.BooleanField(read_only=True)

    title = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    terms = serializers.SerializerMethodField()

    full_name = serializers.SerializerMethodField()
    channel_wallpaper = serializers.SerializerMethodField()
    quest = serializers.SerializerMethodField()

    def get_type(self, obj):
        return "public_official"

    def get_state(self, obj):
        try:
            return dict(US_STATES)[obj.state]
        except KeyError:
            return obj.state

    def get_full_name(self, obj):
        if obj.full_name is None:
            return None
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

    def get_quest(self, obj):
        from sagebrew.sb_quests.neo_models import Quest
        from sagebrew.sb_quests.serializers import QuestSerializer
        # We use object_uuid here instead of owner_username as none of the
        # public officials have a owner
        quest = None
        query = 'MATCH (o:PublicOfficial {object_uuid: "%s"})-' \
                '[:IS_HOLDING]->(quest:Quest) ' \
                'RETURN quest' % obj.object_uuid
        res, _ = db.cypher_query(query)
        if res.one:
            quest = res.one
        if quest is not None:
            quest = QuestSerializer(Quest.inflate(quest)).data
        return quest
