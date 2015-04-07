import markdown

from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel.exception import CypherException

from sb_docstore.utils import get_vote_count
from plebs.serializers import PlebSerializerNeo, UserSerializer


class QuestionSerializerNeo(serializers.Serializer):
    object_uuid = serializers.CharField(read_only=True)
    href = serializers.HyperlinkedIdentityField(view_name='question-detail',
                                                lookup_field="object_uuid")
    content = serializers.CharField()
    title = serializers.CharField(required=False)
    last_edited_on = serializers.DateTimeField(read_only=True)
    upvotes = serializers.CharField(read_only=True)
    downvotes = serializers.CharField(read_only=True)
    vote_count = serializers.SerializerMethodField()
    owner_object = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    solution_count = serializers.CharField(read_only=True)
    html_content = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    is_closed = serializers.BooleanField(read_only=True)
    to_be_deleted = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        # TODO should store in dynamo and then spawn task to store in Neo
        pass

    def update(self, instance, validated_data):
        # TODO get from dynamo and then spawn task to store in Neo
        pass

    def get_owner_object(self, obj):
        request = self.context['request']
        if isinstance(obj, dict) is True:
            return obj
        try:
            owner = obj.owned_by.all()[0]
        except(CypherException, IOError, IndexError):
            return None
        html = request.QUERY_PARAMS.get('html', 'false').lower()
        expand = request.QUERY_PARAMS.get('expand', "false").lower()
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
        except(CypherException, IOError, IndexError):
            return None
        html = request.QUERY_PARAMS.get('html', 'false').lower()
        expand = request.QUERY_PARAMS.get('expand', "false").lower()
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
        return reverse('question_detail_page',
                       kwargs={'question_uuid': obj.object_uuid},
                       request=self.context['request'])

    def get_vote_count(self, obj):
        upvotes = get_vote_count(obj.object_uuid, 1)
        downvotes = get_vote_count(obj.object_uuid, 0)
        return str(upvotes - downvotes)

    def get_html_content(self, obj):
        return markdown.markdown(obj.content)