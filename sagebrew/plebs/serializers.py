from django.contrib.auth import update_session_auth_hash

from rest_framework import serializers
from rest_framework.reverse import reverse

from api.utils import spawn_task, request_to_api
from sb_registration.utils import create_user_util
from plebs.neo_models import Address

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
    new_password = serializers.CharField(max_length=128, required=False,
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
        # TODO @tyler we need to test if this password logic works or if we
        # should only set password if something is passed
        if instance.check_password(validated_data.get('password', "")) is True:
            instance.set_password(validated_data.get(
                'new_password', validated_data.get('password', "")))
            update_session_auth_hash(self.context['request'], instance)
        instance.save()
        spawn_task(task_func=pleb_user_update, task_param={
            "username": instance.username,
            "first_name": instance.first_name,
            "last_name": instance.last_name, "email": instance.email
        })
        return instance


class PlebSerializerNeo(serializers.Serializer):
    base_user = serializers.SerializerMethodField()
    href = serializers.HyperlinkedIdentityField(
        view_name='profile-detail', lookup_field="username")
    profile_pic = serializers.CharField(read_only=True)
    reputation = serializers.IntegerField(read_only=True)
    url = serializers.SerializerMethodField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def get_url(self, obj):
        return reverse(
            'profile_page', kwargs={'pleb_username': obj.username},
            request=self.context['request'])

    def get_base_user(self, obj):
        request = self.context['request']
        expand = request.query_params.get('expand', 'false').lower()
        username = obj.username
        user_url = reverse(
            'user-detail', kwargs={'username': username}, request=request)
        if expand == "true":
            response = request_to_api(user_url, obj.username,
                                      req_method="GET")
            return response.json()
        else:
            return user_url


class AddressSerializer(serializers.Serializer):
    object_uuid = serializers.CharField(read_only=True)
    href = serializers.HyperlinkedIdentityField(read_only=True,
                                               view_name="address-detail",
                                               lookup_field="object_uuid")
    street = serializers.CharField(max_length=125)
    street_additional = serializers.CharField(required=False, allow_blank=True,
                                              allow_null=True, max_length=125)
    city = serializers.CharField(max_length=150)
    state = serializers.CharField(max_length=50)
    postal_code = serializers.CharField(max_length=15)
    country = serializers.CharField(allow_null=True, required=False)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    congressional_district = serializers.CharField()
    validated = serializers.BooleanField(required=False, read_only=True)

    def create(self, validated_data):
        return Address(**validated_data).save()

    def update(self, instance, validated_data):
        instance.street = validated_data.get('street', instance.street)
        instance.street_additional = validated_data.get(
            'street_additional', instance.street_additional)
        instance.city = validated_data.get("city", instance.city)
        instance.state = validated_data.get("state", instance.state)
        instance.postal_code = validated_data.get("postal_code",
                                                  instance.postal_code)
        instance.country = validated_data.get("country", instance.country)
        instance.congressional_district = validated_data.get(
            "congressional_district", instance.congressional_district)
        instance.latitude = validated_data.get("latitude", instance.latitude)
        instance.longitude = validated_data.get("longitude",
                                                instance.longitude)
        # TODO need to re-evaluate where their district is and all that good
        # stuff when they update. @Tyler we should rediscuss the address
        # hashing and how this will affect that.
        instance.save()
        return instance