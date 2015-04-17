from rest_framework import serializers


class ActionSerializer(serializers.Serializer):
    resource = serializers.CharField()
    permission = serializers.CharField()
    # href = serializers.HyperlinkedIdentityField()


class PrivilegeSerializer(serializers.Serializer):
    name = serializers.CharField()
