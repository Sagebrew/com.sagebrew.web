import us

from unidecode import unidecode
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.reverse import reverse

from neomodel import db, DoesNotExist

from api.serializers import SBSerializer
from api.utils import spawn_task, gather_request_data
from sb_quests.serializers import QuestSerializer
from sb_quests.neo_models import Quest

from .neo_models import Address, Pleb
from .tasks import (create_pleb_task, pleb_user_update, determine_pleb_reps,
                    update_address_location)


def generate_username(first_name, last_name):
    # NOTE the other implementation of this is still in use and should be
    # updated if this version is. /sb_registration/utils.py generate_username
    users_count = User.objects.filter(first_name__iexact=first_name).filter(
        last_name__iexact=last_name).count()
    username = "%s_%s" % (first_name.lower(), last_name.lower())
    if len(username) > 30:
        username = username[:30]
        users_count = User.objects.filter(username__iexact=username).count()
        if users_count > 0:
            username = username[:(30 - users_count)] + str(users_count)
    elif len(username) < 30 and users_count == 0:
        username = "%s_%s" % (
            (''.join(e for e in first_name if e.isalnum())).lower(),
            (''.join(e for e in last_name if e.isalnum())).lower())
    else:
        username = "%s_%s%d" % (
            (''.join(e for e in first_name if e.isalnum())).lower(),
            (''.join(e for e in last_name if e.isalnum())).lower(),
            users_count)
    try:
        username = unidecode(unicode(username, "utf-8"))
    except TypeError:
        # Handles cases where the username is already in unicode format
        username = unidecode(username)
    return username


class ReputationNotificationValidator:
    """
    This class will attempt to get the parent instance of the serializer and
    set self.object_uuid to it, this allows it to validate that there are no
    solutions to a question when attempting to update the tile of a question,
    but also allows creation of the question by setting self.object_uuid to
    None if there is not an instance in the serializer.
    """
    def __init__(self):
        pass

    def __call__(self, value):
        if not value or value is None:
            message = 'Cannot change reputation_update_seen to false.'
            raise serializers.ValidationError(message)
        return value


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
    email = serializers.EmailField(required=True, write_only=True,
                                   validators=[UniqueValidator(
                                       queryset=User.objects.all(),
                                       message="Sorry looks like that email is "
                                               "already taken.")],)
    password = serializers.CharField(max_length=128, required=True,
                                     write_only=True,
                                     style={'input_type': 'password'})
    new_password = serializers.CharField(max_length=128, required=False,
                                         write_only=True,
                                         style={'input_type': 'password'})
    birthday = serializers.DateTimeField(write_only=True)
    href = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

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
                    date_of_birth=birthday)
        pleb.save()
        # TODO Should move this out to the endpoint to remove circular
        # dependencies
        cache.delete(pleb.username)
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

    def get_profile(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return reverse('profile-detail', kwargs={'username': obj.username},
                       request=request)

    def get_href(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        return reverse(
            'user-detail', kwargs={'username': obj.username}, request=request)


class PlebSerializerNeo(SBSerializer):
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    email_verified = serializers.BooleanField(read_only=True)
    completed_profile_info = serializers.BooleanField(read_only=True)
    # determine whether to show a notification about reputation change
    reputation_update_seen = serializers.BooleanField(
        required=False, validators=[ReputationNotificationValidator()])
    href = serializers.SerializerMethodField()

    # These are read only because we force users to use a different endpoint
    # to set them, as it requires us to manipulate the uploaded image
    profile_pic = serializers.CharField(required=False)
    wallpaper_pic = serializers.CharField(required=False)

    reputation = serializers.IntegerField(read_only=True)
    reputation_change = serializers.ReadOnlyField()

    # Don't think we need restrictions as that logic should be done for the
    # front end and privileges/actions that are not allowed to be used shouldn't
    # show up in the list. @Tyler what do you think?
    privileges = serializers.SerializerMethodField()
    donations = serializers.SerializerMethodField()
    sagebrew_donations = serializers.SerializerMethodField()
    actions = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    quest = serializers.SerializerMethodField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        """
        Only profile_pic and wallpaper_pic are allowed to be updated using
        this endpoint. This is because any other editing of the pleb
        that occurs should also update the user so use v1/users/
        to update anything else in the pleb.

        :param instance:
        :param validated_data:
        :return:
        """
        request, _, _, _, _ = gather_request_data(self.context)
        update_time = request.data.get('update_time', False)
        instance.profile_pic = validated_data.get('profile_pic',
                                                  instance.profile_pic)
        instance.wallpaper_pic = validated_data.get('wallpaper_pic',
                                                    instance.wallpaper_pic)
        instance.reputation_update_seen = validated_data.get(
            'reputation_update_seen', instance.reputation_update_seen)
        if update_time:
            instance.last_counted_vote_node = instance.vote_from_last_refresh
        instance.save()
        instance.refresh()
        cache.set(instance.username, instance)
        return instance

    def get_id(self, obj):
        return obj.username

    def get_type(self, obj):
        return "profile"

    def get_url(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return reverse(
            'profile_page', kwargs={'pleb_username': obj.username},
            request=request)

    def get_privileges(self, obj):
        return obj.get_privileges()

    def get_actions(self, obj):
        return obj.get_actions()

    def get_href(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return reverse(
            'profile-detail', kwargs={'username': obj.username},
            request=request)

    def get_donations(self, obj):
        return obj.get_donations()

    def get_sagebrew_donations(self, obj):
        return obj.get_sagebrew_donations()

    def get_quest(self, obj):
        request, expand, _, _, _ = gather_request_data(
            self.context, expand_param=self.context.get('expand', None))
        try:
            quest = Quest.get(owner_username=obj.username)
        except(Quest.DoesNotExist, DoesNotExist):
            return None
        if expand == 'true' and quest is not None:
            return QuestSerializer(quest, context={'request': request}).data
        return quest.owner_username

    def get_is_following(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        if request is not None:
            return obj.is_following(request.user.username)
        return False


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
    congressional_district = serializers.IntegerField()
    validated = serializers.BooleanField(required=False, read_only=True)

    def create(self, validated_data):
        validated_data['state'] = us.states.lookup(validated_data['state']).name
        address = Address(**validated_data).save()
        address.set_encompassing()
        return address

    def update(self, instance, validated_data):
        request = self.context.get('request', None)
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
        instance.save()
        cache.delete('%s_possible_house_representatives' %
                     request.user.username)
        cache.delete('%s_possible_senators' % request.user.username)
        spawn_task(task_func=determine_pleb_reps, task_param={
            "username": self.context['request'].user.username,
        })
        spawn_task(task_func=update_address_location,
                   task_param={"object_uuid": instance.object_uuid})
        return instance

    def get_href(self, obj):
        request, expand, _, _, _ = gather_request_data(self.context)
        return reverse(
            "address-detail", kwargs={'object_uuid': obj.object_uuid},
            request=request)


class AddressExportSerializer(serializers.Serializer):
    street = serializers.CharField(max_length=125)
    street_additional = serializers.CharField(required=False, allow_blank=True,
                                              allow_null=True, max_length=125)
    city = serializers.CharField(max_length=150)
    state = serializers.CharField(max_length=50)
    postal_code = serializers.CharField(max_length=15)
    country = serializers.CharField(allow_null=True, required=False)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    congressional_district = serializers.IntegerField()


class FriendRequestSerializer(SBSerializer):
    seen = serializers.BooleanField()
    time_sent = serializers.DateTimeField(read_only=True)
    time_seen = serializers.DateTimeField(allow_null=True, required=False,
                                          read_only=True)
    response = serializers.CharField(required=False, allow_null=False,
                                     allow_blank=False)
    from_user = serializers.SerializerMethodField()
    to_user = serializers.SerializerMethodField()

    def get_type(self, obj):
        return "friend_request"

    def get_from_user(self, obj):
        query = 'MATCH (a:FriendRequest {object_uuid: "%s"})-' \
                '[:REQUEST_FROM]->(b:Pleb) RETURN b' % obj.object_uuid
        res, col = db.cypher_query(query)

        return PlebSerializerNeo(Pleb.inflate(res[0][0])).data

    def get_to_user(self, obj):
        query = 'MATCH (a:FriendRequest {object_uuid: "%s"})-' \
                '[:REQUEST_TO]->(b:Pleb) RETURN b' % obj.object_uuid
        res, col = db.cypher_query(query)

        return PlebSerializerNeo(Pleb.inflate(res[0][0])).data


class PlebExportSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()

    address = serializers.SerializerMethodField()

    def get_address(self, obj):
        return AddressExportSerializer(obj.get_address()).data


class PoliticalPartySerializer(SBSerializer):
    names = serializers.ListField(
        child=serializers.CharField(max_length=126),
    )


class InterestsSerializer(SBSerializer):
    interests = serializers.ListField(
        child=serializers.CharField(max_length=126),
    )
