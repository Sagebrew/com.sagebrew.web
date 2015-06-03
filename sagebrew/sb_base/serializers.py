import markdown

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import CypherException, db

from api.serializers import SBSerializer
from api.utils import gather_request_data

from plebs.serializers import PlebSerializerNeo
from plebs.neo_models import Pleb
from sb_campaigns.serializers import CampaignSerializer
from sb_campaigns.neo_models import Campaign


class VotableContentSerializer(SBSerializer):
    # TODO Deprecate in favor of id based on
    # http://jsonapi.org/format/#document-structure-resource-objects
    object_uuid = serializers.CharField(read_only=True)

    content = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)

    upvotes = serializers.SerializerMethodField()
    downvotes = serializers.SerializerMethodField()
    vote_count = serializers.SerializerMethodField()
    # Need to figure out how we want to handle these user specific items
    # Maybe if no user is provided we just return None or don't include?
    vote_type = serializers.SerializerMethodField()

    view_count = serializers.SerializerMethodField()

    profile = serializers.SerializerMethodField()

    url = serializers.SerializerMethodField()

    def get_profile(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        owner_username = obj.owner_username
        if expand == "true":
            owner = Pleb.get(username=owner_username)
            profile_dict = PlebSerializerNeo(
                owner, context={'request': request}).data
        else:
            profile_dict = reverse('profile-detail',
                                   kwargs={"username": owner_username},
                                   request=request)
        return profile_dict

    def get_url(self, obj):
        # TODO should change this to raise NotImplementedError and implement
        # get_url down the line
        return None

    def get_vote_count(self, obj):
        return obj.get_vote_count()

    def get_vote_type(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        if request is None:
            return None
        return obj.get_vote_type(request.user.username)

    def get_upvotes(self, obj):
        return obj.get_upvote_count()

    def get_downvotes(self, obj):
        return obj.get_downvote_count()

    def get_view_count(self, obj):
        return obj.get_view_count()


class ContentSerializer(VotableContentSerializer):
    last_edited_on = serializers.DateTimeField(read_only=True)
    # Need to figure out how we want to handle these user specific items
    # Maybe if no user is provided we just return None or don't include?
    flagged_by = serializers.SerializerMethodField()

    def get_flagged_by(self, obj):
        return obj.get_flagged_by()


class MarkdownContentSerializer(ContentSerializer):
    is_closed = serializers.BooleanField(read_only=True)
    html_content = serializers.SerializerMethodField()

    def get_html_content(self, obj):
        if obj.content is not None:
            return markdown.markdown(obj.content.replace('&gt;', '>'))
        else:
            return ""


class TitledContentSerializer(MarkdownContentSerializer):
    title = serializers.CharField(required=False,
                                  min_length=15, max_length=140)

    def validate_title(self, value):
        if (self.object_uuid is not None):
            message = 'Cannot edit Title when there have ' \
                      'already been solutions provided'
            raise serializers.ValidationError(message)
        return value


class CampaignAttributeSerializer(SBSerializer):
    """
    This serializer is inherited from by both the GoalSerializer and
    RoundSerializer. We can have our logic for getting campaigns in
    this serializer so we don't have to repeat code. We can also use this
    for any object we need in the future that needs to get the campaign it is
    related to.
    """
    campaign = serializers.SerializerMethodField()

    def get_campaign(self, obj):
        request, _, _, relation, expedite = gather_request_data(self.context)
        if expedite == 'true':
            return None
        query = 'MATCH (o:`%s` {object_uuid:"%s"})-[:ASSOCIATED_WITH]-' \
                '(c:Campaign) RETURN c.object_uuid' % (obj.get_child_label(),
                                                       obj.object_uuid)
        res, col = db.cypher_query(query)
        if not res:
            return None
        if relation == 'hyperlink':
            return reverse('campaign-detail',
                           kwargs={'object_uuid': res[0][0]},
                           request=request)
        return res[0][0]
