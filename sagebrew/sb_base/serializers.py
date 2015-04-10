import markdown

from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.reverse import reverse

from plebs.serializers import PlebSerializerNeo, UserSerializer


class ContentSerializer(serializers.Serializer):
    object_uuid = serializers.CharField(read_only=True)

    content = serializers.CharField()

    created = serializers.DateTimeField(read_only=True)
    last_edited_on = serializers.DateTimeField(read_only=True)

    upvotes = serializers.SerializerMethodField()
    downvotes = serializers.SerializerMethodField()
    vote_type = serializers.SerializerMethodField()
    vote_count = serializers.SerializerMethodField()

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
        raise NotImplementedError

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


class MarkdownContentSerializer(ContentSerializer):
    is_closed = serializers.IntegerField(read_only=True)
    to_be_deleted = serializers.IntegerField(read_only=True)
    html_content = serializers.SerializerMethodField()

    def get_html_content(self, obj):
        if obj.content is not None:
            return markdown.markdown(obj.content)
        else:
            return ""