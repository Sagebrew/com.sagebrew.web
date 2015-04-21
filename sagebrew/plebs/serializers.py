from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel.exception import DoesNotExist

from api.serializers import SBSerializer
from api.utils import spawn_task, request_to_api, gather_request_data

from .neo_models import Address, Pleb, BetaUser
from .tasks import create_pleb_task, pleb_user_update


def generate_username(first_name, last_name):
    users_count = User.objects.filter(first_name__iexact=first_name).filter(
        last_name__iexact=last_name).count()
    username = "%s_%s" % (first_name.lower(), last_name.lower())
    if len(username) > 30:
        username = username[:30]
        users_count = User.objects.filter(username__iexact=username).count()
        if users_count > 0:
            username = username[:(30 - len(users_count))] + str(users_count)
    elif len(username) < 30 and users_count == 0:
        username = "%s_%s" % (
            (''.join(e for e in first_name if e.isalnum())).lower(),
            (''.join(e for e in last_name if e.isalnum())).lower())
    else:
        username = "%s_%s%d" % (
            (''.join(e for e in first_name if e.isalnum())).lower(),
            (''.join(e for e in last_name if e.isalnum())).lower(),
            users_count)
    return username


def check_beta_user(email, pleb):
    try:
        beta_user = BetaUser.nodes.get(email=email)
        pleb.beta_user.connect(beta_user)
    except(BetaUser.DoesNotExist, DoesNotExist):
        pass


class BetaUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    invited = serializers.BooleanField()
    signup_date = serializers.DateTimeField()


class UserSerializer(SBSerializer):
    username = serializers.CharField(max_length=30, read_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=True)
    # We can probably add something to the retrieve that if a friend wants
    # to request viewing this the user can allow them to.
    email = serializers.EmailField(required=True, write_only=True)
    password = serializers.CharField(max_length=128, required=True,
                                     write_only=True,
                                     style={'input_type': 'password'})
    new_password = serializers.CharField(max_length=128, required=False,
                                         write_only=True,
                                         style={'input_type': 'password'})
    birthday = serializers.DateTimeField(write_only=True)
    href = serializers.SerializerMethodField()

    def create(self, validated_data):
        username = generate_username(validated_data['first_name'],
                                     validated_data['last_name'])
        birthday = validated_data.pop('birthday', None)

        user = User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password'], username=username)
        user.save()
        pleb = Pleb(email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                    birthday=birthday)
        pleb.save()
        check_beta_user(user.email, pleb)
        # TODO Should move this out to the endpoint to remove circular
        # dependencies
        spawn_task(task_func=create_pleb_task,
                   task_param={
                       "user_instance": user, "birthday": birthday,
                       "password": validated_data['password']})
        return user

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
        # TODO Should move this out to the endpoint to remove circular
        # dependencies. Like we do in sb_questions/endpoints.py create
        spawn_task(task_func=pleb_user_update, task_param={
            "username": instance.username,
            "first_name": instance.first_name,
            "last_name": instance.last_name, "email": instance.email
        })
        return instance

    def get_id(self, obj):
        return obj.username

    def get_href(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        return reverse(
            'user-detail', kwargs={'username': obj.username}, request=request)


class PlebSerializerNeo(SBSerializer):
    base_user = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()

    # These are read only because we force users to use a different endpoint
    # to set them, as it requires us to manipulate the uploaded image
    profile_pic = serializers.CharField(read_only=True)
    wallpaper_pic = serializers.CharField(read_only=True)

    reputation = serializers.IntegerField(read_only=True)

    # Don't think we need restrictions as that logic should be done for the
    # front end and privileges/actions that are not allowed to be used shouldn't
    # show up in the list. @Tyler what do you think?
    privileges = serializers.SerializerMethodField()
    actions = serializers.SerializerMethodField()

    url = serializers.SerializerMethodField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def get_id(self, obj):
        return obj.username

    def get_type(self, obj):
        return "profile"

    def get_url(self, obj):
        try:
            request = self.context['request']
        except KeyError:
            request = None
        return reverse(
            'profile_page', kwargs={'pleb_username': obj.username},
            request=request)

    def get_base_user(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)

        username = obj.username
        user_url = reverse(
            'user-detail', kwargs={'username': username}, request=request)
        if expand == "true":
            response = request_to_api(user_url, request.user.username,
                                      req_method="GET")
            return response.json()
        else:
            return user_url

    def get_privileges(self, obj):
        res = obj.get_privileges()
        request, expand, expand_array, _, _ = gather_request_data(self.context)

        # Future proofing this as this is not a common use case but we can still
        # give users the ability to do so
        if expand == "true" and "privileges" in expand_array:
            priv_array = []
            for row in res:
                privilege_url = reverse("privilege-detail",
                                        kwargs={"name": row},
                                        request=request)
                response = request_to_api(privilege_url, request.user.username,
                                          req_method="GET")
                priv_array.append(response.json())
            return priv_array
        else:
            return res

    def get_actions(self, obj):
        return obj.get_actions()

    def get_href(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        return reverse(
            'profile-detail', kwargs={'username': obj.username},
            request=request)


class AddressSerializer(SBSerializer):
    object_uuid = serializers.CharField(read_only=True)
    href = serializers.SerializerMethodField()
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

    def get_href(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        return reverse(
            "address-detail", kwargs={'object_uuid': obj.object_uuid},
            request=request)

class FriendRequestSerializer(SBSerializer):
    seen = serializers.BooleanField()
    time_sent = serializers.DateTimeField(read_only=True)
    time_seen = serializers.DateTimeField(allow_null=True, required=False)
    response = serializers.CharField(required=False)
