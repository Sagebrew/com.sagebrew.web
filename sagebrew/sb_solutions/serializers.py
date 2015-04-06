import markdown

from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel.exception import CypherException

from sb_docstore.utils import get_vote_count
from plebs.serializers import PlebSerializerNeo, UserSerializer

from .neo_models import SBSolution


class SolutionSerializerDynamo(serializers.Serializer):
    object_uuid = serializers.CharField()
    # TODO we can keep parent_object internally but externally we should discuss
    # making this less generic and a hyperlink related field
    # This should then enable us to combine the serializers rather than needing
    # multiple
    parent_object = serializers.CharField()
    href = serializers.HyperlinkedIdentityField(view_name='solution-detail',
                                                lookup_field="object_uuid")
    content = serializers.CharField()

    last_edited_on = serializers.DateTimeField(read_only=True)
    upvotes = serializers.CharField(read_only=True)
    downvotes = serializers.CharField(read_only=True)
    vote_count = serializers.CharField(read_only=True)
    owner = serializers.HyperlinkedRelatedField(queryset=User.objects.all(),
                                                view_name='user-detail',
                                                lookup_field="username")
    created = serializers.DateTimeField(read_only=True)
    # May want to change this to a url field and then query from the front end
    # all the comments associated with a given solution
    #comments = serializers.ListSerializer(child=serializers.DictField())
    # Auto gathered from request.user.email
    solution_owner_email = serializers.CharField()
    # TODO need to make edits into a list of http urls that allow us to query
    # the solution endpoint and grab all the edits
    # edits = HyperlinkedRelatedField(
    #    queryset=Solution.nodes.all(),
    #    view_name='solution-detail', many=True, lookup_field='object_uuid')
    # TODO with new layout this should no longer be necessary
    object_type = serializers.CharField(read_only=True)
    html_content = serializers.CharField(read_only=True)

    def create(self, validated_data):
        # TODO should store in dynamo and then spawn task to store in Neo
        pass

    def update(self, instance, validated_data):
        # TODO get from dynamo and then spawn task to store in Neo
        pass


class SolutionSerializerNeo(serializers.Serializer):
    object_uuid = serializers.CharField(read_only=True)
    href = serializers.HyperlinkedIdentityField(view_name='solution-detail',
                                                lookup_field="object_uuid")
    content = serializers.CharField()

    last_edited_on = serializers.DateTimeField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    upvotes = serializers.CharField(read_only=True)
    vote_count = serializers.SerializerMethodField()
    downvotes = serializers.CharField(read_only=True)
    owner_object = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    is_closed = serializers.BooleanField(read_only=True)
    to_be_deleted = serializers.BooleanField(read_only=True)
    html_content = serializers.SerializerMethodField()

    def create(self, validated_data):
        # TODO should store in dynamo and then spawn task to store in Neo
        solution = SBSolution(**validated_data).save()
        return solution

    def update(self, instance, validated_data):
        # TODO get from dynamo and then spawn task to store in Neo
        pass

    def get_vote_count(self, obj):
        return obj.get_vote_count()

    def get_html_content(self, obj):
        if obj.content is not None:
            return markdown.markdown(obj.content)
        else:
            return ""

    def get_owner_object(self, obj):
        # TODO this should probably be a util or something since it's copied
        # and pasted everywhere....
        request = self.context['request']
        if isinstance(obj, dict) is True:
            return obj
        try:
            owner = obj.owned_by.all()[0]
        except(CypherException, IOError, IndexError):
            return None
        html = request.query_params.get('html', 'false').lower()
        expand = request.query_params.get('expand', "false").lower()
        if html == "true":
            expand = "true"
        if expand == "true":
            owner_user = User.objects.get(username=owner.username)
            owner_dict = UserSerializer(
                owner_user, context={'request': self.context['request']}).data
        else:
            owner_dict = reverse('user-detail',
                                 kwargs={"username": owner.username},
                                 request=request)
        return owner_dict

    def get_profile(self, obj):
        # TODO this should probably be a util or something since it's copied
        # and pasted everywhere....
        request = self.context['request']
        if isinstance(obj, dict) is True:
            return obj
        try:
            owner = obj.owned_by.all()[0]
        except(CypherException, IOError, IndexError):
            return None
        html = request.query_params.get('html', 'false').lower()
        expand = request.query_params.get('expand', "false").lower()
        if html == "true":
            expand = "true"
        if expand == "true":
            profile_dict = PlebSerializerNeo(
                owner, context={'request': request}).data
        else:
            profile_dict = reverse('profile-detail',
                                   kwargs={"username": owner.username},
                                   request=request)
        return profile_dict