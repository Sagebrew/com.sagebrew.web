import pytz
from datetime import datetime

from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework import serializers
from rest_framework.reverse import reverse

from api.utils import gather_request_data
from sb_base.serializers import ContentSerializer
from plebs.serializers import PlebSerializerNeo, UserSerializer
from plebs.neo_models import Pleb

from .neo_models import Post


class PostSerializerNeo(ContentSerializer):
    href = serializers.HyperlinkedIdentityField(view_name='post-detail',
                                                lookup_field="object_uuid")
    wall_owner = serializers.SerializerMethodField()
    wall_owner_profile = serializers.SerializerMethodField()

    def create(self, validated_data):
        request = self.context["request"]
        owner = cache.get(request.user.username)
        if owner is None:
            owner = Pleb.nodes.get(username=request.user.username)
            cache.set(request.user.username, owner)
        wall_owner = validated_data.pop('wall_owner', None)
        post = Post(**validated_data).save()
        post.owned_by.connect(owner)
        owner.posts.connect(post)
        wall = wall_owner.get_wall()
        post.posted_on_wall.connect(wall)
        wall.posts.connect(post)

        return post

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.last_edited_on = datetime.now(pytz.utc)
        instance.save()

        return instance

    def get_url(self, obj):
        # TODO can we add anchors or should we make the one off post page?
        owner = obj.owned_by.all()[0]
        return reverse('profile_page',
                       kwargs={'pleb_username': owner.username},
                       request=self.context.get('request', None))

    def get_wall_owner(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        if isinstance(obj, dict) is True:
            return obj
        owner_wall = obj.posted_on_wall.all()[0]
        wall_owner = owner_wall.owned_by.all()[0]
        if expand == "true":
            owner_user = User.objects.get(username=wall_owner.username)
            owner_dict = UserSerializer(
                owner_user, context={'request': request}).data
        else:
            owner_dict = reverse('user-detail',
                                 kwargs={"username": wall_owner.username},
                                 request=request)
        return owner_dict

    def get_wall_owner_profile(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        if isinstance(obj, dict) is True:
            return obj
        owner_wall = obj.posted_on_wall.all()[0]
        wall_owner = owner_wall.owned_by.all()[0]
        if expand == "true":
            profile_dict = PlebSerializerNeo(
                wall_owner, context={'request': request}).data
        else:
            profile_dict = reverse('profile-detail',
                                   kwargs={"username": wall_owner.username},
                                   request=request)
        return profile_dict
