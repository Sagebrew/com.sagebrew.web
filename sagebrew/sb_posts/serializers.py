import bleach
import pytz
from datetime import datetime

from rest_framework import serializers
from rest_framework.reverse import reverse

from api.utils import gather_request_data
from sb_base.serializers import ContentSerializer
from plebs.serializers import PlebSerializerNeo
from plebs.neo_models import Pleb
from sb_uploads.neo_models import UploadedObject

from .neo_models import Post


class PostSerializerNeo(ContentSerializer):
    href = serializers.HyperlinkedIdentityField(view_name='post-detail',
                                                lookup_field="object_uuid")
    images = serializers.ListField(write_only=True, required=False)

    uploaded_objects = serializers.SerializerMethodField()
    wall_owner_profile = serializers.SerializerMethodField()

    def create(self, validated_data):
        request = self.context["request"]
        owner = Pleb.get(request.user.username)
        wall_owner = validated_data.pop('wall_owner_profile', None)
        content = validated_data.pop('content')
        images = validated_data.pop('images', [])
        post = Post(owner_username=owner.username,
                    content=bleach.clean(content),
                    wall_owner_username=wall_owner.username,
                    **validated_data).save()
        post.owned_by.connect(owner)
        owner.posts.connect(post)
        wall = wall_owner.get_wall()
        post.posted_on_wall.connect(wall)
        wall.posts.connect(post)
        for image in images:
            image_node = UploadedObject.nodes.get(object_uuid=image)
            post.uploaded_objects.connect(image_node)
            image_node.related_content.connect(post)
        return post

    def update(self, instance, validated_data):
        instance.content = bleach.clean(validated_data.get(
            'content', instance.content))
        instance.last_edited_on = datetime.now(pytz.utc)
        instance.save()

        return instance

    def get_url(self, obj):
        request, _, _, _, expedite = gather_request_data(self.context)
        if expedite == "true":
            return None
        return obj.get_url(request)

    def get_wall_owner_profile(self, obj):
        request, expand, _, _, expedite = gather_request_data(self.context)
        if self.context.get('force_expand', False):
            return PlebSerializerNeo(
                obj.get_wall_owner_profile(), context={'request': request}).data
        if expedite == "true":
            return None
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

    def get_uploaded_objects(self, obj):
        return obj.get_uploaded_objects()
