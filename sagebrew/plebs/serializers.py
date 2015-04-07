from rest_framework import serializers
from rest_framework.reverse import reverse

from api.utils import spawn_task
from sb_registration.utils import create_user_util

from .tasks import pleb_user_update


class BetaUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    invited = serializers.BooleanField()
    signup_date = serializers.DateTimeField()


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30, read_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=True)
    # We can probably add something to the retrieve that if a friend wants
    # to request viewing this the user can allow them to.
    email = serializers.EmailField(required=True, write_only=True)
    password = serializers.CharField(max_length=128, required=True,
                                     write_only=True)
    birthday = serializers.DateTimeField(write_only=True)
    href = serializers.HyperlinkedIdentityField(view_name='user-detail',
                                                lookup_field="username")

    def create(self, validated_data):
        response = create_user_util(**validated_data)
        if isinstance(response, Exception) is True:
            return response
        return response["user"]

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name',
                                                 instance.first_name)
        instance.last_name = validated_data.get('last_name',
                                                instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.set_password(validated_data.get('password', instance.email))
        instance.save()
        spawn_task(task_func=pleb_user_update, task_param={
            "username": instance.username,
            "first_name": instance.first_name,
            "last_name": instance.last_name, "email": instance.email
        })
        return instance


class PlebSerializerNeo(serializers.Serializer):
    base_user = serializers.HyperlinkedIdentityField(view_name='user-detail',
                                                     lookup_field="username")
    href = serializers.HyperlinkedIdentityField(
        view_name='profile-detail', lookup_field="username")
    profile_pic = serializers.CharField(read_only=True)
    reputation = serializers.IntegerField(read_only=True)
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse(
            'profile_page', kwargs={'pleb_username': obj.username},
            request=self.context['request'])

    def update():
        pass