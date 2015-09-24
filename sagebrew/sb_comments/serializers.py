import bleach
import pytz
from uuid import uuid1
from datetime import datetime

from django.conf import settings

from rest_framework.reverse import reverse
from rest_framework import serializers

from neomodel import db

from api.utils import request_to_api, gather_request_data
from sb_base.serializers import ContentSerializer
from sb_base.neo_models import SBContent

from .neo_models import Comment


class CommentSerializer(ContentSerializer):
    parent_type = serializers.CharField(read_only=True)

    href = serializers.SerializerMethodField()
    comment_on = serializers.SerializerMethodField()

    def create(self, validated_data):
        request = self.context["request"]
        owner = validated_data.pop('owner', None)
        parent_object = validated_data.pop('parent_object', None)
        validated_data['content'] = bleach.clean(
            validated_data.get('content', ''))
        validated_data['owner_username'] = owner.username
        # we use get_child_label() here because the parent_object is an
        # instance of SBContent and not the required Post, Solution,
        # Question this gets us the proper label of the node
        uuid = str(uuid1())
        href = reverse("comment-detail", kwargs={'object_uuid': uuid},
                       request=request)
        url = parent_object.url
        comment = Comment(parent_type=parent_object.get_child_label().lower(),
                          url=url, href=href, object_uuid=uuid,
                          **validated_data).save()
        comment.owned_by.connect(owner)
        owner.comments.connect(comment)
        parent_object.comments.connect(comment)
        if parent_object.visibility == "public":
            comment.visibility = "public"
            comment.save()
        comment.comment_on.connect(parent_object)

        return comment

    def update(self, instance, validated_data):
        instance.content = bleach.clean(
            validated_data.get('content', instance.content))
        instance.last_edited_on = datetime.now(pytz.utc)
        instance.save()
        return instance

    def get_href(self, obj):
        return reverse('comment-detail',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=self.context.get('request', None))

    def get_url(self, obj):
        request, _, _, _, expedite = gather_request_data(self.context)
        # If expedite is true it is assumed the calling function handles this
        # functionality
        if obj.url is not None:
            return obj.url
        if expedite != "true":
            parent_object = get_parent_object(obj.object_uuid)
            parent_url = reverse(
                '%s-detail' % parent_object.get_child_label().lower(),
                kwargs={'object_uuid': parent_object.object_uuid},
                request=request)
            if request is not None:
                # Shouldn't need to check for anon because if user is anon
                # comments will return an empty list for private content.
                # It will return the proper information for public info.
                response = request_to_api(parent_url, request.user.username,
                                          req_method="GET")
            else:
                parent_url = "%s%s" % (settings.WEB_ADDRESS, parent_url)
                response = request_to_api(parent_url,
                                          obj.owner_username,
                                          req_method="GET")
            return response.json()['url']
        return None

    def get_comment_on(self, obj):
        request, expand, expand_array, relations, expedite =\
            gather_request_data(self.context)
        # If expedite is true it is assumed the calling function handles this
        # functionality
        if expedite != "true":
            parent_object = get_parent_object(obj.object_uuid)
            parent_info = reverse(
                '%s-detail' % parent_object.get_child_label().lower(),
                kwargs={'object_uuid': parent_object.object_uuid},
                request=request)
            # Future proofing this as this is not a common use case but we can
            # still give users the ability to do so
            if expand == "true" and "comment_on" in expand_array and \
                    request is not None:
                response = request_to_api(parent_info, request.user.username,
                                          req_method="GET")
                parent_info = response.json()

            return parent_info
        else:
            return None


def get_parent_object(object_uuid):
    try:
        query = "MATCH (a:Comment {object_uuid:'%s'})-[:COMMENT_ON]->" \
                "(b:SBContent) RETURN b" % object_uuid
        res, col = db.cypher_query(query)
        return SBContent.inflate(res.one)
    except IndexError:
        return None
