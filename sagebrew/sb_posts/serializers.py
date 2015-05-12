import bleach
import pytz
from datetime import datetime

from rest_framework import serializers
from rest_framework.reverse import reverse

from api.utils import gather_request_data
from sb_base.serializers import ContentSerializer
from plebs.serializers import PlebSerializerNeo
from plebs.neo_models import Pleb

from .neo_models import Post


class PostSerializerNeo(ContentSerializer):
    href = serializers.HyperlinkedIdentityField(view_name='post-detail',
                                                lookup_field="object_uuid")
    wall_owner_profile = serializers.SerializerMethodField()

    def create(self, validated_data):
        request = self.context["request"]
        owner = Pleb.get(request.user.username)
        wall_owner = validated_data.pop('wall_owner_profile', None)
        validated_data['content'] = bleach.clean(
            validated_data.get('content', ''))
        post = Post(**validated_data).save()
        post.owned_by.connect(owner)
        owner.posts.connect(post)
        wall = wall_owner.get_wall()
        post.posted_on_wall.connect(wall)
        wall.posts.connect(post)

        return post

    def update(self, instance, validated_data):
        instance.content = bleach.clean(validated_data.get(
            'content', instance.content))
        instance.last_edited_on = datetime.now(pytz.utc)
        instance.save()

        return instance

    def get_url(self, obj):
        return obj.get_url(self.context.get('request', None))

    def get_wall_owner_profile(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        if isinstance(obj, dict) is True:
            return obj
        wall_owner = obj.get_wall_owner_profile()
        if expand == "true":
            profile_dict = PlebSerializerNeo(
                wall_owner, context={'request': request}).data
        else:
            profile_dict = reverse('profile-detail',
                                   kwargs={"username": wall_owner.username},
                                   request=request)
        return profile_dict
