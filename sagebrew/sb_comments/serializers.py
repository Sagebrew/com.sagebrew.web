from rest_framework.reverse import reverse
from rest_framework import serializers

from sb_base.serializers import ContentSerializer

from .neo_models import Comment


class CommentSerializer(ContentSerializer):
    comment_on = serializers.SerializerMethodField()

    def create(self, validated_data):
        owner = validated_data.pop('owner', None)
        parent_object = validated_data.pop('parent_object', None)
        comment = Comment(**validated_data).save()
        if owner is not None:
            comment.owned_by.connect(owner)
            owner.comments.connect(comment)
        if parent_object is not None:
            parent_object.comments.connect(comment)
            comment.comment_on.connect(parent_object)

        return comment

    def update(self, instance, validated_data):
        instance.meta = validated_data.get('meta', instance.meta)
        instance.name = validated_data.get('name', instance.name)
        instance.assets = validated_data.get('assets', instance.assets)
        instance.project_type = validated_data.get("project_type",
                                                   instance.project_type)
        instance.combo_product = validated_data.get("combo_product",
                                                    instance.combo_product)
        instance.save()
        return instance

    def get_url(self, obj):
        request = self.context.get('request', None)
        try:
            parent_object = obj.comment_on.all()[0]
        except(IndexError):
            return None
        return reverse('%s-detail' % parent_object.get_child_label(),
                       kwargs={'object_uuid': parent_object.object_uuid},
                       request=request)

    def get_comment_on(self, obj):
        request = self.context.get('request', None)
        try:
            parent_object = obj.comment_on.all()[0]
        except(IndexError):
            return None

        return reverse('%s-detail' % parent_object.get_child_label(),
                       kwargs={'object_uuid': parent_object.object_uuid},
                       request=request)