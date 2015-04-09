from rest_framework.reverse import reverse
from rest_framework import serializers

from neomodel.exception import CypherException

from sb_base.serializers import ContentSerializer
from .neo_models import SBComment


class CommentSerializer(ContentSerializer):
    comment_on = serializers.SerializerMethodField()

    def create(self, validated_data):
        # Connection of the comment to the object it is on is handled in the
        # create method of the endpoint as it is easier to gather the related
        # object from there.
        owner = validated_data.pop('owner', None)
        comment = SBComment(**validated_data).save()
        comment.owned_by.connect(owner)
        owner.comments.connect(comment)

        return comment

    def update(self, instance, validated_data):
        # TODO get from dynamo and then spawn task to store in Neo
        pass

    def get_url(self, obj):
        # TODO @tyler is there a cleaner way you can think to do this?
        try:
            parent_object = obj.comment_on.all()[0]
        except(IOError, IndexError, CypherException):
            return None
        return reverse('%s-detail' % parent_object.sb_name,
                       kwargs={'object_uuid': parent_object.object_uuid},
                       request=self.context['request'])

    def get_comment_on(self, obj):
        try:
            parent_object = obj.comment_on.all()[0]
        except(IOError, IndexError, CypherException):
            return None
        return reverse('%s-detail' % parent_object.sb_name,
                       kwargs={'object_uuid': parent_object.object_uuid},
                       request=self.context['request'])