from rest_framework import serializers

from api.serializers import SBSerializer


class TagSerializer(SBSerializer):
    name = serializers.CharField()
    href = serializers.HyperlinkedIdentityField(view_name="tag-detail",
                                                lookup_field="name")
