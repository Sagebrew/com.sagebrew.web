from rest_framework import serializers


class SolutionSerializer(serializers.Serializer):
    uuid = serializers.CharField()
    parent_object = serializers.CharField()
    content = serializers.CharField()
    last_edited_on = serializers.CharField()
    up_vote_number = serializers.CharField()
    down_vote_number = serializers.CharField()
    object_vote_count = serializers.CharField()
    # Auto generated from request.user.get_full_name()
    # solution_owner_name = serializers.CharField()
    solution_owner_url = serializers.CharField()
    time_created = serializers.CharField()
    comments = serializers.CharField()
    # Auto gathered from request.user.email
    # solution_owner_email = serializers.CharField()
    # TODO need to make edits into a list of http urls that allow us to query
    # the solution endpoint and grab all the edits
    # edits = HyperlinkedRelatedField(
    #    queryset=Solution.nodes.all(),
    #    view_name='solution-detail', many=True, lookup_field='object_uuid')
    object_type = serializers.CharField()

    def create(self, validated_data):
        # TODO should store in dynamo and then spawn task to store in Neo
        pass

    def update(self, instance, validated_data):
        # TODO get from dynamo and then spawn task to store in Neo
        pass