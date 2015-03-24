from rest_framework import serializers

from .neo_models import SBSolution


class SolutionSerializerDynamo(serializers.Serializer):
    object_uuid = serializers.CharField()
    # TODO we can keep parent_object internally but externally we should discuss
    # making this less generic and a hyperlink related field
    # This should then enable us to combine the serializers rather than needing
    # multiple
    parent_object = serializers.CharField()
    href = serializers.HyperlinkedIdentityField(view_name='solutions-detail',
                                                lookup_field="object_uuid",
                                                id_field="object_uuid")
    content = serializers.CharField()

    last_edited_on = serializers.DateTimeField(read_only=True)
    up_vote_number = serializers.CharField(read_only=True)
    down_vote_number = serializers.CharField(read_only=True)
    object_vote_count = serializers.CharField(read_only=True)
    # Auto generated from request.user.get_full_name()
    # TODO probably just want to point to the owner and get the attributes
    # from there
    solution_owner_name = serializers.CharField()
    solution_owner_url = serializers.CharField()
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
    href = serializers.HyperlinkedIdentityField(view_name='solutions-detail',
                                                lookup_field="object_uuid",
                                                id_field="object_uuid")
    content = serializers.CharField()

    last_edited_on = serializers.DateTimeField(read_only=True)
    up_vote_number = serializers.CharField(read_only=True)
    down_vote_number = serializers.CharField(read_only=True)

    def create(self, validated_data):
        # TODO should store in dynamo and then spawn task to store in Neo
        solution = SBSolution(**validated_data).save()
        return solution

    def update(self, instance, validated_data):
        # TODO get from dynamo and then spawn task to store in Neo
        pass