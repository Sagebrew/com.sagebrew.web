from rest_framework import serializers

from sb_comments.serializers import CommentSerializer


class SolutionSerializer(serializers.Serializer):
    object_uuid = serializers.CharField()
    parent_object = serializers.CharField()
    content = serializers.CharField()
    last_edited_on = serializers.DateTimeField()
    up_vote_number = serializers.CharField()
    down_vote_number = serializers.CharField()
    object_vote_count = serializers.CharField()
    # Auto generated from request.user.get_full_name()
    solution_owner_name = serializers.CharField()
    solution_owner_url = serializers.CharField()
    time_created = serializers.DateTimeField()
    # May want to change this to a url field and then query from the front end
    # all the comments associated with a given solution
    #comments = CommentSerializer(many=True)
    # Auto gathered from request.user.email
    solution_owner_email = serializers.CharField()
    # TODO need to make edits into a list of http urls that allow us to query
    # the solution endpoint and grab all the edits
    # edits = HyperlinkedRelatedField(
    #    queryset=Solution.nodes.all(),
    #    view_name='solution-detail', many=True, lookup_field='object_uuid')
    object_type = serializers.CharField()
    html_content = serializers.CharField()

    def create(self, validated_data):
        # TODO should store in dynamo and then spawn task to store in Neo
        pass

    def update(self, instance, validated_data):
        # TODO get from dynamo and then spawn task to store in Neo
        pass