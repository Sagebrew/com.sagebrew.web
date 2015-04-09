import markdown

from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel.exception import CypherException

from plebs.serializers import PlebSerializerNeo, UserSerializer

from .neo_models import SBSolution


class SolutionSerializerNeo(serializers.Serializer):
    object_uuid = serializers.CharField(read_only=True)
    href = serializers.HyperlinkedIdentityField(view_name='solution-detail',
                                                lookup_field="object_uuid")
    content = serializers.CharField()

    last_edited_on = serializers.DateTimeField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    upvotes = serializers.CharField(read_only=True)
    vote_count = serializers.SerializerMethodField()
    downvotes = serializers.CharField(read_only=True)
    owner_object = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    is_closed = serializers.BooleanField(read_only=True)
    to_be_deleted = serializers.BooleanField(read_only=True)
    html_content = serializers.SerializerMethodField()

    def create(self, validated_data):
        # TODO should store in dynamo and then spawn task to store in Neo
        solution = SBSolution(**validated_data).save()
        return solution

    def update(self, instance, validated_data):
        # TODO get from dynamo and then spawn task to store in Neo
        pass

    def get_vote_count(self, obj):
        return obj.get_vote_count()

    def get_html_content(self, obj):
        if obj.content is not None:
            return markdown.markdown(obj.content)
        else:
            return ""

    def get_owner_object(self, obj):
        # TODO this should probably be a util or something since it's copied
        # and pasted everywhere....
        request = self.context['request']
        if isinstance(obj, dict) is True:
            return obj
        try:
            owner = obj.owned_by.all()[0]
        except(CypherException, IOError, IndexError):
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
        # TODO this should probably be a util or something since it's copied
        # and pasted everywhere....
        request = self.context['request']
        if isinstance(obj, dict) is True:
            return obj
        try:
            owner = obj.owned_by.all()[0]
        except(CypherException, IOError, IndexError):
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