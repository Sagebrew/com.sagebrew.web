from django.conf import settings

from intercom import Admin, Intercom
from neomodel import DoesNotExist
from rest_framework import serializers

from api.utils import spawn_task
from plebs.neo_models import Pleb
from sb_base.tasks import create_email


def validate_to_or_from(value):
    Intercom.app_id = settings.INTERCOM_APP_ID
    Intercom.app_api_key = settings.INTERCOM_API_KEY
    value_type = value.get('type', None)
    user_id = value.get('user_id', None)
    passed_id = value.get('id', None)
    if value_type != "user" and value_type != "admin":
        raise serializers.ValidationError("The only valid values for 'type' "
                                          "are 'user' and 'admin'")
    if value_type == "user" and user_id is None:
        raise serializers.ValidationError("Must provide the 'user_id' key "
                                          "when attempting to send a message "
                                          "to or from a user")
    if value_type == "admin":
        if passed_id is None:
            raise serializers.ValidationError("Must provide the 'id' key when "
                                              "attempting to send a message "
                                              "to or from an admin")

        admins = Admin.all()
        if str(passed_id) not in [admin.id for admin in admins]:
            raise serializers.ValidationError(
                "%s is not a valid admin ID" % passed_id)
    try:
        Pleb.get(username=user_id)
    except (Pleb.DoesNotExist, DoesNotExist):
        if value_type != 'admin':
            raise serializers.ValidationError(
                "Pleb %s Does Not Exist" % user_id)

    return value


class IntercomMessageSerializer(serializers.Serializer):
    message_type = serializers.CharField()
    subject = serializers.CharField()
    body = serializers.CharField()
    template = serializers.ChoiceField(choices=[
        ('plain', 'plain'), ('personal', 'personal'),
        ('company', 'company'), ('announcement', 'announcement')
    ])
    from_user = serializers.DictField(child=serializers.CharField(),
                                      validators=[validate_to_or_from])
    to_user = serializers.DictField(child=serializers.CharField(),
                                    validators=[validate_to_or_from])

    def create(self, validated_data):
        from_user = validated_data.pop('from_user', None)
        to_user = validated_data.pop('to_user', None)
        validated_data['from'] = from_user
        validated_data['to'] = to_user
        spawn_task(task_func=create_email, task_param=validated_data)
        validated_data['from_user'] = from_user
        validated_data['to_user'] = to_user
        return validated_data
