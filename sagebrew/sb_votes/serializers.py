from rest_framework.reverse import reverse
from rest_framework import serializers
from neomodel import db

from api.utils import request_to_api, gather_request_data
from api.serializers import SBSerializer
from sb_base.neo_models import SBContent


class VoteSerializer(SBSerializer):
    # Need to add validator here or in Votable Content that limits the amount
    # of flags that can be placed on a piece of content from a single user to
    # one
    vote_type = serializers.BooleanField()
    url = serializers.SerializerMethodField()
    vote_on = serializers.SerializerMethodField()

    def create(self, validated_data):
        return None

    def update(self, instance, validated_data):
        return None

    def get_vote_on(self, obj):
        request, _, _, _, expedite = gather_request_data(self.context)
        if expedite == "true":
            return None
        parent_object = get_vote_parent(obj.object_uuid)
        parent_href = reverse(
            '%s-detail' % parent_object.get_child_label().lower(),
            kwargs={'object_uuid': parent_object.object_uuid},
            request=request)

        response = request_to_api(parent_href, request.user.username,
                                  req_method="GET")
        return response.json()['href']

    def get_url(self, obj):
        request, _, _, _, expedite = gather_request_data(self.context)
        if expedite == "true":
            return None
        request = self.context.get('request', None)
        parent_object = get_vote_parent(obj.object_uuid)
        parent_href = reverse(
            '%s-detail' % parent_object.get_child_label().lower(),
            kwargs={'object_uuid': parent_object.object_uuid},
            request=request)

        response = request_to_api(parent_href, request.user.username,
                                  req_method="GET")
        return response.json()['url']


def get_vote_parent(object_uuid):
    try:
        query = "MATCH (a:Vote {object_uuid:'%s'})-[:VOTE_ON]->" \
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
