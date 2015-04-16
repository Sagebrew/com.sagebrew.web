import markdown

from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.reverse import reverse

from plebs.serializers import PlebSerializerNeo, UserSerializer
from plebs.neo_models import Pleb


class VotableContentSerializer(serializers.Serializer):
    object_uuid = serializers.CharField(read_only=True)
    content = serializers.CharField()

    created = serializers.DateTimeField(read_only=True)

    upvotes = serializers.SerializerMethodField()
    downvotes = serializers.SerializerMethodField()
    vote_count = serializers.SerializerMethodField()
    # Need to figure out how we want to handle these user specific items
    # Maybe if no user is provided we just return None or don't include?
    vote_type = serializers.SerializerMethodField()

    view_count = serializers.SerializerMethodField()

    owner_object = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    url = serializers.SerializerMethodField()

    def get_owner_object(self, obj):
        request = self.context['request']
        if isinstance(obj, dict) is True:
            return obj
        try:
            owner = obj.owned_by.all()[0]
        except(IOError):
            return None
        html = request.query_params.get('html', 'false').lower()
        expand = request.query_params.get('expand', "false").lower()
        if html == "true":
            expand = "true"
        if expand == "true":
            owner_user = User.objects.get(username=owner.username)
            owner_dict = UserSerializer(
                owner_user, context={'request': self.context['request']}).data
        else:
            owner_dict = reverse('user-detail',
                                 kwargs={"username": owner.username},
                                 request=request)
        return owner_dict

    def get_profile(self, obj):
        request = self.context['request']
        if isinstance(obj, dict) is True:
            return obj
        try:
            owner = obj.owned_by.all()[0]
        except(IOError):
            return None
        html = request.query_params.get('html', 'false').lower()
        expand = request.query_params.get('expand', "false").lower()
        if html == "true":
            expand = "true"
        if expand == "true":
            profile_dict = PlebSerializerNeo(
                owner, context={'request': request}).data
        else:
            profile_dict = reverse('profile-detail',
                                   kwargs={"username": owner.username},
                                   request=request)
        return profile_dict

    def get_url(self, obj):
        # TODO should change this to raise NotImplementedError and implement
        # get_url down the line
        return None

    def get_vote_count(self, obj):
        return obj.get_vote_count()

    def get_vote_type(self, obj):
        return obj.get_vote_type(self.context['request'].user.username)

    def get_upvotes(self, obj):
        return obj.get_upvote_count()

    def get_downvotes(self, obj):
        return obj.get_downvote_count()

    def get_view_count(self, obj):
        return obj.get_view_count()


class ContentSerializer(VotableContentSerializer):
    last_edited_on = serializers.DateTimeField(read_only=True)
    # Need to figure out how we want to handle these user specific items
    # Maybe if no user is provided we just return None or don't include?
    flagged_by = serializers.SerializerMethodField()

    def get_flagged_by(self, obj):
        res = obj.get_flagged_by()
        return [Pleb.inflate(row[0]).username for row in res]


class MarkdownContentSerializer(ContentSerializer):
    is_closed = serializers.BooleanField(read_only=True)
    html_content = serializers.SerializerMethodField()

    def get_html_content(self, obj):
        if obj.content is not None:
            return markdown.markdown(obj.content)
        else:
            return ""