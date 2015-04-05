from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel.exception import CypherException

from plebs.serializers import PlebSerializerNeo, UserSerializer

from .neo_models import SBComment


class CommentSerializer(serializers.Serializer):
    object_uuid = serializers.CharField(read_only=True)
    object_type = serializers.CharField(read_only=True)
    parent_object = serializers.CharField(read_only=True)
    content = serializers.CharField()
    last_edited_on = serializers.DateTimeField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    vote_count = serializers.CharField(read_only=True)
    upvotes = serializers.IntegerField(read_only=True)
    downvotes = serializers.IntegerField(read_only=True)
    owner_object = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    # TODO add owner pleb and utilize def perform_create(self, serializer)
    # to store off owner of comment

    def create(self, validated_data):
        owner = validated_data.pop('owner', None)
        comment = SBComment(**validated_data).save()
        comment.owned_by.connect(owner)
        return comment

    def update(self, instance, validated_data):
        # TODO get from dynamo and then spawn task to store in Neo
        pass

    def get_owner_object(self, obj):
        request = self.context['request']
        if isinstance(obj, dict) is True:
            owner = obj["owner"]
        else:
            try:
                owner = obj.owned_by.all()[0]
            except(CypherException, IOError, IndexError):
                return None
        html = request.query_params.get('html', 'false').lower()
        expand = request.query_params.get('expand', "false").lower()
        if html == "true":
            expand = "true"
        print expand
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