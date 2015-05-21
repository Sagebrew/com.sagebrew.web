import bleach
import markdown

from rest_framework.reverse import reverse
from rest_framework import serializers
from neomodel import db

from api.utils import request_to_api
from sb_base.neo_models import SBContent
from sb_base.serializers import VotableContentSerializer

from .neo_models import Flag


class FlagSerializer(VotableContentSerializer):
    # This inherits from Votable Content because a flag is going to be voted
    # on by the Admin council and will have similar information corresponding
    # to it
    # Need to add validator here or in Votable Content that limits the amount
    # of flags that can be placed on a piece of content from a single user to
    # one
    flag_on = serializers.SerializerMethodField()
    content = serializers.CharField(required=False)
    flag_type = serializers.ChoiceField([('explicit', 'Explicit'),
                                         ('duplicate', 'Duplicate'),
                                         ('spam', "Spam"),
                                         ("other", "Other")])
    html_content = serializers.SerializerMethodField()

    def get_html_content(self, obj):
        if obj.content is not None:
            return markdown.markdown(obj.content)
        else:
            return ""

    def create(self, validated_data):
        owner = validated_data.pop('owner', None)
        parent_object = validated_data.pop('parent_object', None)
        validated_data['content'] = bleach.clean(
            validated_data.get('content', ''))
        validated_data['owner_username'] = owner.username
        flag = Flag(**validated_data).save()
        flag.owned_by.connect(owner)
        owner.flags.connect(flag)
        parent_object.flags.connect(flag)
        flag.flag_on.connect(parent_object)
        parent_object.flagged_by.connect(owner)

        return flag

    def update(self, instance, validated_data):
        # Currently don't support updating flags
        pass

    def get_flag_on(self, obj):
        request = self.context.get('request', None)
        if request is None:
            return None
        parent_object = get_flag_parent(obj.object_uuid)
        parent_href = reverse(
            '%s-detail' % parent_object.get_child_label().lower(),
            kwargs={'object_uuid': parent_object.object_uuid},
            request=request)
        response = request_to_api(parent_href, request.user.username,
                                  req_method="GET")
        return response.json()['href']

    def get_url(self, obj):
        request = self.context.get('request', None)
        if request is None:
            return None
        parent_object = get_flag_parent(obj.object_uuid)
        parent_href = reverse(
            '%s-detail' % parent_object.get_child_label().lower(),
            kwargs={'object_uuid': parent_object.object_uuid},
            request=request)

        response = request_to_api(parent_href, request.user.username,
                                  req_method="GET")
        return response.json()['url']


def get_flag_parent(object_uuid):
    try:
        query = "MATCH (a:Flag {object_uuid:'%s'})-[:FLAG_ON]->" \
                "(b:SBContent) RETURN b" % (object_uuid)
        res, col = db.cypher_query(query)
        try:
            content = SBContent.inflate(res[0][0])
        except ValueError:
            # This exception was added while initially implementing the fxn and
            # may not be possible in production. What happened was multiple
            # flags/votes got associated with a piece of content causing an
            # array to be returned instead of a single object which is handled
            # above. This should be handled now but we should verify that
            # the serializers ensure this singleness prior to removing this.
            content = SBContent.inflate(res[0][0][0])
        return content
    except(IndexError):
        return None
