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
    content = serializers.SerializerMethodField()
    title = serializers.CharField(required=False)
    last_edited_on = serializers.DateTimeField(read_only=True)
    upvotes = serializers.CharField(read_only=True)
    downvotes = serializers.CharField(read_only=True)
    vote_count = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    solution_count = serializers.CharField(read_only=True)

    def create(self, validated_data):
        # TODO should store in dynamo and then spawn task to store in Neo
        pass

    def update(self, instance, validated_data):
        # TODO get from dynamo and then spawn task to store in Neo
        pass

    def get_owner(self, obj):
        request = self.context['request']
        if isinstance(obj, dict) is True:
            return obj
        try:
            owner = obj.owned_by.all()[0]
        except(CypherException, IOError, IndexError):
            return None
        expand = request.QUERY_PARAMS.get('expand', "false")
        if expand == "true":
            profile = PlebSerializerNeo(
                owner, context={'request': request}).data
            owner_user = User.objects.get(username=owner.username)
            owner_dict = UserSerializer(
                owner_user, context={'request': self.context['request']}).data
            owner_dict["profile"] = profile
        else:
            owner_dict = reverse('user-detail',
                                 kwargs={"username": owner.username},
                                 request=request)
        return owner_dict

    def get_content(self, obj):
        most_recent = obj.get_most_recent_edit()
        if isinstance(most_recent, Exception):
            return None
        return most_recent.content

    def get_url(self, obj):
        return reverse('question_detail_page',
                       kwargs={'question_uuid': obj.object_uuid},
                       request=self.context['request'])

    def get_vote_count(self, obj):
        upvotes = get_vote_count(obj.object_uuid, 1)
        downvotes = get_vote_count(obj.object_uuid, 0)
        return str(upvotes - downvotes)