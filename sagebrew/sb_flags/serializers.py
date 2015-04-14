import markdown

from rest_framework.reverse import reverse
from rest_framework import serializers
from neomodel import db

from api.utils import request_to_api
from sb_base.neo_models import SBContent
from sb_base.serializers import VotableContentSerializer

from .neo_models import Flag


class FlagSerializer(VotableContentSerializer):
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
            content = SBContent.inflate(res[0][0][0])
        return content
    except(IndexError):
        return None