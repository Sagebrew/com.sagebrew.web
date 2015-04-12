import pytz
from datetime import datetime

from rest_framework.reverse import reverse
from rest_framework import serializers

from neomodel import db

from api.utils import request_to_api
from sb_base.serializers import ContentSerializer
from sb_base.neo_models import SBContent

from .neo_models import Comment


class CommentSerializer(ContentSerializer):
    href = serializers.HyperlinkedIdentityField(view_name='comment-detail',
                                                lookup_field="object_uuid",
                                                lookup_url_kwarg="comment_uuid")
    comment_on = serializers.SerializerMethodField()

    def create(self, validated_data):
        owner = validated_data.pop('owner', None)
        parent_object = validated_data.pop('parent_object', None)
        comment = Comment(**validated_data).save()
        comment.owned_by.connect(owner)
        owner.comments.connect(comment)
        parent_object.comments.connect(comment)
        comment.comment_on.connect(parent_object)

        return comment

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.last_edited_on = datetime.now(pytz.utc)
        instance.save()
        return instance

    def get_url(self, obj):
        request = self.context.get('request', None)
        parent_object = get_parent_object(obj.object_uuid)
        parent_url = reverse(
            '%s-detail' % parent_object.get_child_label().lower(),
            kwargs={'object_uuid': parent_object.object_uuid},
            request=request)
        response = request_to_api(parent_url, request.user.username,
                                  req_method="GET")
        return response.json()['url']

    def get_comment_on(self, obj):
        request = self.context.get('request', None)
        expand = request.query_params.get('expand', "false").lower()
        expand_array = request.query_params.get('expand_attr', [])
        parent_object = get_parent_object(obj.object_uuid)
        parent_info = reverse(
            '%s-detail' % parent_object.get_child_label().lower(),
            kwargs={'object_uuid': parent_object.object_uuid},
            request=request)
        # Future proofing this as this is not a common use case but we can still
        # give users the ability to do so
        if expand == "true" and "comment_on" in expand_array:
            response = request_to_api(parent_info, request.user.username,
                                      req_method="GET")
            parent_info = response.json()

        return parent_info


def get_parent_object(object_uuid):
    try:
        query = "MATCH (a:Comment {object_uuid:'%s'})-[:COMMENT_ON]->" \
                "(b:SBContent) RETURN b" % (object_uuid)
        res, col = db.cypher_query(query)
        return SBContent.inflate(res[0][0])
    except(IndexError):
        return None
