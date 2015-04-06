import markdown

from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel.exception import CypherException

from sb_docstore.utils import get_vote_count
from plebs.serializers import PlebSerializerNeo, UserSerializer

from .neo_models import SBPost


class PostSerializerNeo(serializers.Serializer):
    object_uuid = serializers.CharField(read_only=True)
    href = serializers.HyperlinkedIdentityField(view_name='post-detail',
                                                lookup_field="object_uuid")
    content = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)
    upvotes = serializers.CharField(read_only=True)
    downvotes = serializers.CharField(read_only=True)
    vote_count = serializers.SerializerMethodField()
    owner_object = serializers.SerializerMethodField()
    # Keeping url as a shortcut, incase the user doesn't want to
    # expand out the profile and gather the url through the profile
    # object.
    url = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    last_edited_on = serializers.DateTimeField(read_only=True)
    wall_owner = serializers.SerializerMethodField()
    wall_owner_profile = serializers.SerializerMethodField()

    def create(self, validated_data):
        owner = validated_data.pop('owner', None)
        wall_owner = validated_data.pop('wall_owner', None)
        post = SBPost(**validated_data).save()
        post.owned_by.connect(owner)
        owner.posts.connect(post)
        try:
            wall = wall_owner.wall.all()[0]
            post.posted_on_wall.connect(wall)
        except(CypherException, IOError, IndexError):
            raise IOError
        return post

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

    def get_url(self, obj):
        # TODO can we add anchors?
        try:
            owner = obj.owned_by.all()[0]
        except(CypherException, IOError, IndexError):
            return None
        return reverse('profile_page',
                       kwargs={'pleb_username': owner.username},
                       request=self.context['request'])

    def get_vote_count(self, obj):
        upvotes = get_vote_count(obj.object_uuid, 1)
        downvotes = get_vote_count(obj.object_uuid, 0)
        return str(upvotes - downvotes)

    def get_wall_owner(self, obj):
        # TODO can we move all this into a util? It's getting copied and pasted
        # in all the serializers and even here has logic extremely similar to
        # get_owner and get_profile.
        request = self.context['request']
        if isinstance(obj, dict) is True:
            return obj
        try:
            owner_wall = obj.posted_on_wall.all()[0]
            wall_owner = owner_wall.owner.all()[0]
        except(CypherException, IOError, IndexError):
            return None
        html = request.query_params.get('html', 'false').lower()
        expand = request.query_params.get('expand', "false").lower()
        if html == "true":
            expand = "true"
        if expand == "true":
            owner_user = User.objects.get(username=wall_owner.username)
            owner_dict = UserSerializer(
                owner_user, context={'request': self.context['request']}).data
        else:
            owner_dict = reverse('user-detail',
                                 kwargs={"username": wall_owner.username},
                                 request=request)
        return owner_dict

    def get_wall_owner_profile(self, obj):
        request = self.context['request']
        if isinstance(obj, dict) is True:
            return obj
        try:
            owner_wall = obj.posted_on_wall.all()[0]
            wall_owner = owner_wall.owner.all()[0]
        except(CypherException, IOError, IndexError):
            return None
        html = request.query_params.get('html', 'false').lower()
        expand = request.query_params.get('expand', "false").lower()
        if html == "true":
            expand = "true"
        if expand == "true":
            profile_dict = PlebSerializerNeo(
                wall_owner, context={'request': request}).data
        else:
            profile_dict = reverse('profile-detail',
                                   kwargs={"username": wall_owner.username},
                                   request=request)
        return profile_dict