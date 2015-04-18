from rest_framework import serializers

from api.serializers import SBSerializer


class ActionSerializer(SBSerializer):
    resource = serializers.CharField()
    permission = serializers.CharField()
    # href = serializers.HyperlinkedIdentityField()


class PrivilegeSerializer(SBSerializer):
    name = serializers.CharField()
    href = serializers.HyperlinkedIdentityField(view_name="privilege-detail",
                                                lookup_field="name")
