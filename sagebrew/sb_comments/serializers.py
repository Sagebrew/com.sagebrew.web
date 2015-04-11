from rest_framework.reverse import reverse
from rest_framework import serializers

from api.utils import spawn_task
from sb_base.utils import get_labels
from sb_base.serializers import ContentSerializer

from .tasks import create_comment_relations
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
        data = {"username": owner.username, "comment": comment.object_uuid,
                "parent_object": parent_object.object_uuid}
        spawn_task(task_func=create_comment_relations, task_param=data)
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
        labels = get_labels(parent_object.__class__.__name__,
                            self.lookup_field,
                            self.kwargs[self.lookup_field])
        # This goes on the assumption that Neo4J returns labels in order of
        # assignment. Since neomodel assigns these in order of inheritance
        # the top most parent being first and the bottom child being last
        # we assume that our actual real commentable object is last.
        object_type = labels[-1].lower()
        return reverse('%s-detail' % object_type,
                       kwargs={'object_uuid': parent_object.object_uuid},
                       request=request)

    def get_comment_on(self, obj):
        request = self.context.get('request', None)
        try:
            parent_object = obj.comment_on.all()[0]
        except(IndexError):
            return None
        return reverse('%s-detail' % parent_object.sb_name,
                       kwargs={'object_uuid': parent_object.object_uuid},
                       request=request)