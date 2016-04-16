from neomodel import DoesNotExist
from rest_framework import serializers

from plebs.neo_models import Pleb


class IntercomMessageSerializer(serializers.Serializer):
    message_type = serializers.CharField()
    subject = serializers.CharField()
    body = serializers.CharField()
    template = serializers.ChoiceField(choices=[
        ('plain', 'plain'), ('personal', 'personal'),
        ('company', 'company'), ('announcement', 'announcement')
    ])
    from_user = serializers.DictField(child=serializers.CharField())
    to_user = serializers.DictField(child=serializers.CharField())

    def validate_to_user(self, value):
        value_type = value.get('type', None)
        user_id = value.get('id', None)
        if value_type is None:
            raise serializers.ValidationError("Must provide the 'type' key")
        if user_id is None:
            raise serializers.ValidationError("Must provide the 'id' key")
        try:
            Pleb.get(username=value['id'])
        except (Pleb.DoesNotExist, DoesNotExist):
            if value_type != 'admin':
                raise serializers.ValidationError(
                    "Pleb %s Does Not Exist" % value['username'])
        if value['type'] != 'user' or value['type'] != 'admin':
            raise serializers.ValidationError("The only valid types for "
                                              "to_user are 'user' and 'admin'")
        return value
