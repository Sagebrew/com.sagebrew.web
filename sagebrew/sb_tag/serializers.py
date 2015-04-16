from rest_framework import serializers


class TagSerializer(serializers.Serializer):
    name = serializers.CharField()
    href = serializers.HyperlinkedIdentityField(view_name="tag-detail",
                                                lookup_field="name")
