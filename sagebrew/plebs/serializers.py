import stripe
from datetime import date
from unidecode import unidecode

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.core.cache import cache
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login, authenticate
from django.conf import settings
from django.utils.text import slugify
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.http import int_to_base36, base36_to_int
from django.utils.crypto import constant_time_compare, salted_hmac

from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator
from rest_framework.reverse import reverse
from rest_framework.exceptions import ValidationError

from py2neo.cypher.error.schema import ConstraintViolation

from neomodel import db, DoesNotExist

from api.serializers import SBSerializer
from api.utils import (smart_truncate, spawn_task,
                       gather_request_data, SBUniqueValidator)
from sb_address.serializers import AddressSerializer, AddressExportSerializer
from sb_base.serializers import (IntercomMessageSerializer,
                                 IntercomEventSerializer)
from sb_quests.serializers import QuestSerializer
from sb_quests.neo_models import Quest

from .neo_models import Pleb
from .tasks import create_wall_task, generate_oauth_info


class EmailAuthTokenGenerator(object):
    """
    This object is created for user email verification
    """

    def make_token(self, user, pleb):
        if pleb is None:
            return None
        return self._make_timestamp_token(user, self._num_days(self._today()),
                                          pleb)

    def check_token(self, user, token, pleb):
        if token is None:
            return False
        try:
            timestamp_base36, hash_key = token.split("-")
        except ValueError:
            return False

        try:
            timestamp = base36_to_int(timestamp_base36)
        except ValueError:
            return False

        if not constant_time_compare(self._make_timestamp_token(
                user, timestamp, pleb), token):
            return False

        if (self._num_days(self._today()) - timestamp) > \
                settings.EMAIL_VERIFICATION_TIMEOUT_DAYS:
            return False

        return True

    def _make_timestamp_token(self, user, timestamp, pleb):
        timestamp_base36 = int_to_base36(timestamp)

        key_salt = "sagebrew.sb_registration.models.EmailAuthTokenGenerator"
        hash_val = "%s%s%s%s%s" % (user.username, user.first_name,
                                   user.last_name, user.email,
                                   pleb.email_verified)

        created_hash = salted_hmac(key_salt, hash_val).hexdigest()[::2]
        return "%s-%s" % (timestamp_base36, created_hash)

    def _num_days(self, dt):
        return (dt - date(2001, 1, 1)).days

    def _today(self):
        return date.today()


def generate_username(first_name, last_name):
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
            message = 'Cannot change this field to false.'
            raise serializers.ValidationError(
                {"reputation_update_seen": message})
        return value


class BetaUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    invited = serializers.BooleanField()
    signup_date = serializers.DateTimeField()


class EmailVerificationSerializer(serializers.Serializer):
    def create(self, validated_data):
        request = self.context.get('request')
        profile = self.context.get('profile')
        user = self.context.get('user')
        if request is None:
            raise ValidationError("Verification email must be "
                                  "requested from application")
        if user is None:
            user = request.user
        if profile is None:
            profile = Pleb.get(
                username=user.username, cache_buster=True)
        token_gen = EmailAuthTokenGenerator()
        message_data = {
            'message_type': 'email',
            'subject': 'Sagebrew Email Verification',
            'body': get_template('email_templates/verification.html').render(
                Context({
                    'first_name': user.first_name,
                    'verification_url': "%s%s%s" % (
                        settings.EMAIL_VERIFICATION_URL,
                        token_gen.make_token(user, profile), '/')
                })),
            'template': "personal",
            'from_user': {
                'type': "admin",
                'id': settings.INTERCOM_ADMIN_ID_DEVON
            },
            'to_user': {
                'type': "user",
                'user_id': user.username
            }
        }
        serializer = IntercomMessageSerializer(
            data=message_data, context={'profile': profile,
                                        'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return {}


class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, validated_data):
        try:
            user = User.objects.get(email=validated_data.get('email'))
        except User.DoesNotExist:
            raise ValidationError("Sorry we couldn't find that address")
        validated_data['user'] = user
        return validated_data

    def create(self, validated_data):
        user = validated_data['user']
        current_site = get_current_site(self.context.get('request'))
        site_name = current_site.name
        context = {
            'email': validated_data['email'],
            'domain': current_site.domain,
            'site_name': site_name,
            'first_name': user.first_name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': default_token_generator.make_token(user)
        }
        message_data = {
            'message_type': 'email',
            'subject': 'Sagebrew Reset Password Request',
            'body': get_template('email_templates/password_reset.html').render(
                Context(context)),
            'template': "personal",
            'from_user': {
                'type': "admin",
                'id': settings.INTERCOM_ADMIN_ID_DEVON
            },
            'to_user': {
                'type': "user",
                'user_id': user.username
            }
        }
        serializer = IntercomMessageSerializer(data=message_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return {"detail": "Reset email successfully sent",
                "status": status.HTTP_200_OK,
                "email": validated_data['email']}


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
        # DEPRECATED use profile create instead
        pass

    def update(self, instance, validated_data):
        # DEPRECATED use profile update instead
        pass

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
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField(read_only=True)
    password = serializers.CharField(max_length=128, required=True,
                                     write_only=True,
                                     style={'input_type': 'password'})
    new_password = serializers.CharField(max_length=128, required=False,
                                         write_only=True,
                                         style={'input_type': 'password'})
    email = serializers.EmailField(required=True, write_only=True,
                                   validators=[SBUniqueValidator(
                                       queryset=User.objects.all(),
                                       message="Sorry looks like that email is "
                                               "already taken.")],)
    date_of_birth = serializers.DateTimeField(required=True, write_only=True)
    occupation_name = serializers.CharField(required=False, allow_null=True,
                                            max_length=240)
    employer_name = serializers.CharField(required=False, allow_null=True,
                                          max_length=240)
    is_verified = serializers.BooleanField(read_only=True)
    email_verified = serializers.BooleanField(read_only=True)
    customer_token = serializers.CharField(write_only=True, required=False)
    stripe_default_card_id = serializers.CharField(write_only=True,
                                                   required=False,
                                                   allow_blank=True)
    mission_signup = serializers.CharField(required=False, allow_blank=True,
                                           allow_null=True)
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
    has_address = serializers.SerializerMethodField()
    name_summary = serializers.SerializerMethodField()

    def create(self, validated_data):
        request, _, _, _, _ = gather_request_data(self.context)
        mission_signup = validated_data.get('mission_signup', None)
        quest_registration = request.session.get('account_type')
        username = generate_username(validated_data['first_name'],
                                     validated_data['last_name'])
        birthday = validated_data.pop('date_of_birth', None)

        user = User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'].lower().strip(),
            password=validated_data['password'], username=username)
        user.save()
        pleb = Pleb(email=user.email.lower().strip(),
                    first_name=user.first_name.title(),
                    last_name=user.last_name.title(),
                    username=user.username,
                    date_of_birth=birthday,
                    occupation_name=validated_data.get('occupation_name', None),
                    employer_name=validated_data.get('employer_name', None),
                    mission_signup=mission_signup).save()
        if mission_signup is None:
            mission_signup = "no"
        # Save so Intercom Event can pass validators, don't just pass the
        # pleb to the event serializer because if something down the chain
        # fails and the pleb never gets saved we could have an endless
        # task running
        pleb.save()
        serializer = IntercomEventSerializer(data={
            "event_name": "signup-%s-mission" % mission_signup,
            "username": username
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if not request.user.is_authenticated():
            user = authenticate(username=user.username,
                                password=validated_data['password'])
            login(request, user)
            if quest_registration is not None:
                request.session['account_type'] = quest_registration
                request.session.set_expiry(1800)
        serializer = EmailVerificationSerializer(
            data={}, context={"profile": pleb, 'request': request,
                              "user": user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        pleb.initial_verification_email_sent = True
        pleb.save()
        interests_serializer = TopicInterestsSerializer(
            data={
                'interests': [
                    interest[0] for interest in settings.TOPICS_OF_INTEREST]},
            context={"request": request})
        interests_serializer.is_valid(raise_exception=True)
        interests_serializer.save()
        spawn_task(task_func=create_wall_task,
                   task_param={"username": user.username})
        spawn_task(task_func=generate_oauth_info,
                   task_param={'username': user.username,
                               'password': validated_data['password']},
                   countdown=20)
        cache.delete(pleb.username)
        return pleb

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
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = settings.STRIPE_API_VERSION
        request, _, _, _, _ = gather_request_data(self.context)
        address = request.data.get('address')
        if address is not None:
            address_serializer = AddressSerializer(
                data=address, context={"request": request})
            address_serializer.is_valid(raise_exception=True)
            address = address_serializer.save()
            query = 'MATCH (a:Pleb) ' \
                    'OPTIONAL MATCH (a)-[r:LIVES_IN]-(:Address) ' \
                    'DELETE r'
            res, _ = db.cypher_query(query)
            instance.address.connect(address)
            instance.determine_reps()

        update_time = request.data.get('update_time', False)
        first_name = validated_data.get('first_name', instance.first_name)
        last_name = validated_data.get('last_name', instance.last_name)
        customer_token = validated_data.pop('customer_token',
                                            instance.customer_token)
        email = validated_data.get('email', instance.email).lower()
        user_obj = User.objects.get(username=instance.username)
        if first_name != user_obj.first_name:
            instance.first_name = first_name
            user_obj.first_name = first_name
        if last_name != user_obj.last_name:
            instance.last_name = last_name
            user_obj.last_name = last_name
        if email != user_obj.email:
            instance.email = email.lower().strip()
            user_obj.email = email.lower().strip()
            if instance.get_quest():
                quest = Quest.get(instance.username, cache_buster=True)
                if quest.stripe_customer_id:
                    customer = \
                        stripe.Customer.retrieve(quest.stripe_customer_id)
                    customer.email = email.lower().strip()
                    customer.save()
        if user_obj.check_password(validated_data.get('password', "")) is True:
            user_obj.set_password(validated_data.get(
                'new_password', validated_data.get('password', "")))
            update_session_auth_hash(self.context.get('request'), user_obj)
        user_obj.save()
        profile_pic = validated_data.get('profile_pic')
        if profile_pic is not None and profile_pic != "":
            instance.profile_pic = validated_data.get('profile_pic',
                                                      instance.profile_pic)
        wallpaper_pic = validated_data.get('wallpaper_pic')
        if wallpaper_pic is not None and wallpaper_pic != "":
            instance.wallpaper_pic = validated_data.get('wallpaper_pic',
                                                        instance.wallpaper_pic)
        instance.occupation_name = validated_data.get('occupation_name',
                                                      instance.occupation_name)
        instance.employer_name = validated_data.get('employer_name',
                                                    instance.employer_name)
        instance.reputation_update_seen = validated_data.get(
            'reputation_update_seen', instance.reputation_update_seen)
        if customer_token is not None:
            # Customers must provide a credit card for us to create a customer
            # with stripe. Get the credit card # and create a customer instance
            # so we can charge it in the future.
            if instance.stripe_customer_id is None:
                customer = stripe.Customer.create(
                    description="Customer %s" % instance.username,
                    card=customer_token,
                    email=instance.email.lower().strip()
                )
                instance.stripe_customer_id = customer['id']
                instance.stripe_default_card_id = customer[
                    'sources']['data'][0]['id']
            else:
                customer = stripe.Customer.retrieve(
                    instance.stripe_customer_id)
                card = customer.sources.create(source=customer_token)
                instance.stripe_default_card_id = card['id']
        instance.stripe_default_card_id = validated_data.get(
            'stripe_default_card_id', instance.stripe_default_card_id)
        if update_time:
            instance.last_counted_vote_node = instance.vote_from_last_refresh

        instance.save()
        instance.update_quest()
        cache.delete(instance.username)
        return super(PlebSerializerNeo, self).update(instance, validated_data)

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
            # Backwards because we don't want to be dependent on the Pleb as
            # the object running the query so the user can follow multiple
            # types of objects. Such as Quest or Plebs.
            return obj.is_following(request.user.username)
        return False

    def get_has_address(self, obj):
        # We provide has_address rather than a full address to allow apps
        # to know if the user has an address or not without compromising
        # our customer's privacy and address.
        query = 'MATCH (p:Pleb {username: "%s"}) ' \
                'OPTIONAL MATCH (p)-[r:LIVES_AT]->(b:Address) ' \
                'RETURN r IS NOT NULL as has_address' % obj.username
        res, _ = db.cypher_query(query)

        return res.one

    def get_name_summary(self, obj):
        full_name = "%s %s" % (obj.first_name, obj.last_name)
        if full_name is not None:
            if len(full_name) > 20:
                return smart_truncate(full_name, 20)
        return full_name


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
    employer_name = serializers.CharField()
    occupation_name = serializers.CharField()

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


class TopicInterestsSerializer(SBSerializer):
    interests = serializers.MultipleChoiceField(
        choices=settings.TOPICS_OF_INTEREST,
        allow_blank=True)

    def create(self, validated_data):
        from sb_tags.neo_models import Tag
        from sb_tags.serializers import TagSerializer
        request, _, _, _, _ = gather_request_data(self.context)
        generated_tags = []
        if request is None:
            raise serializers.ValidationError(
                "Must perform creation from web request")
        for tag in validated_data['interests']:
            try:
                query = 'MATCH (profile:Pleb {username: "%s"}), ' \
                        '(tag:Tag {name: "%s"}) ' \
                        'CREATE UNIQUE (profile)-[:INTERESTED_IN]->(tag) ' \
                        'RETURN tag' % (request.user.username, slugify(tag))
                res, _ = db.cypher_query(query)
                generated_tags.append(TagSerializer(Tag.inflate(res.one)).data)
            except(ConstraintViolation, Exception):
                pass
        cache.delete(request.user.username)
        return generated_tags
