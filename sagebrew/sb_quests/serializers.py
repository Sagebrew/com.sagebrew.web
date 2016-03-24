import pytz
import time
import stripe
from datetime import datetime
from stripe.error import InvalidRequestError
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.core.cache import cache

from rest_framework import serializers, status
from rest_framework.reverse import reverse

from neomodel import db
from neomodel.exception import DoesNotExist

from api.serializers import SBSerializer
from api.utils import (gather_request_data, spawn_task, clean_url,
                       empty_text_to_none)
from plebs.neo_models import Pleb
from sb_privileges.tasks import check_privileges
from sb_locations.neo_models import Location
from sb_search.utils import remove_search_object

from .neo_models import (Position, Quest)


class QuestSerializer(SBSerializer):
    active = serializers.BooleanField(required=False)
    title = serializers.CharField(required=False, allow_blank=True)
    about = serializers.CharField(required=False, allow_blank=True,
                                  max_length=128)
    facebook = serializers.URLField(required=False, allow_blank=True)
    linkedin = serializers.URLField(required=False, allow_blank=True)
    youtube = serializers.URLField(required=False, allow_blank=True)
    twitter = serializers.URLField(required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True)
    wallpaper_pic = serializers.CharField(required=False)
    profile_pic = serializers.CharField(required=False)
    owner_username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    stripe_token = serializers.CharField(write_only=True, required=False)
    customer_token = serializers.CharField(write_only=True, required=False)
    tos_acceptance = serializers.BooleanField(required=False)
    stripe_account_type = serializers.ChoiceField(
        required=False,
        choices=[('business', "Business"), ('individual', "Individual")],)
    account_owner = serializers.CharField(required=False, allow_blank=True)
    stripe_default_card_id = serializers.CharField(write_only=True,
                                                   required=False,
                                                   allow_blank=True)
    ein = serializers.CharField(write_only=True, required=False,
                                allow_blank=True)
    routing_number = serializers.CharField(write_only=True, required=False)
    account_number = serializers.CharField(write_only=True, required=False)
    ssn = serializers.CharField(write_only=True, required=False)
    promotion_key = serializers.CharField(write_only=True, required=False)
    account_type = serializers.ChoiceField(
        required=False,
        choices=[('paid', "Paid"), ('free', "Free"),
                 ('promotion', "Promotion")])
    account_verified = serializers.ChoiceField(
        read_only=True,
        choices=[('unverified', "Unverified"), ('pending', "Pending"),
                 ('verified', "Verified")])
    account_verification_fields_needed = serializers.ListField(read_only=True)
    account_verification_details = serializers.CharField(read_only=True)
    url = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()
    updates = serializers.SerializerMethodField()
    is_editor = serializers.SerializerMethodField()
    is_moderator = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    completed_stripe = serializers.SerializerMethodField()
    completed_customer = serializers.SerializerMethodField()
    missions = serializers.SerializerMethodField()
    total_donation_amount = serializers.SerializerMethodField()

    def create(self, validated_data):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        request = self.context.get('request', None)
        account_type = validated_data.get('account_type', "free")
        tos_acceptance = validated_data.get('tos_acceptance', False)
        owner = Pleb.get(username=request.user.username)
        if owner.get_quest():
            raise serializers.ValidationError(
                detail={"detail": "You may only have one Quest!",
                        "developer_message": "",
                        "status_code": status.HTTP_400_BAD_REQUEST})
        default_title = "%s %s" % (owner.first_name, owner.last_name)
        quest = Quest(first_name=owner.first_name, last_name=owner.last_name,
                      owner_username=owner.username, object_uuid=owner.username,
                      profile_pic=owner.profile_pic,
                      account_type=account_type, title=default_title).save()

        quest.owner.connect(owner)
        quest.editors.connect(owner)
        quest.moderators.connect(owner)
        account = stripe.Account.create(managed=True, country="US",
                                        email=owner.email)
        quest.stripe_id = account['id']
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        account.legal_entity.additional_owners = []
        if tos_acceptance:
            account.tos_acceptance.ip = ip
            account.tos_acceptance.date = int(time.time())
            quest.account_verified_date = datetime.now(pytz.utc)
            quest.tos_acceptance = True
        quest.save()
        account.save()
        # Potential optimization in combining these utilizing a transaction
        # Added these to ensure that the user has intercom when they hit the
        # Quest page for the first time. The privilege still is fired through
        # the spawn_task as a backup and to ensure all connections are made
        # correctly
        epoch_date = datetime(1970, 1, 1, tzinfo=pytz.utc)
        current_time = float((datetime.now(pytz.utc) -
                              epoch_date).total_seconds())
        query = 'MATCH (pleb:Pleb {username: "%s"}) WITH pleb ' \
                'MATCH (privilege:Privilege {name: "quest"}) WITH ' \
                'pleb, privilege ' \
                'MATCH (action:SBAction {resource: "intercom", ' \
                'permission: "write"}) WITH ' \
                'pleb, privilege, action CREATE UNIQUE ' \
                '(action)<-[:CAN {active: true, gained_on: %f}]-(pleb)' \
                '-[r:HAS {active: true, gained_on: %f}]->(privilege) ' \
                'RETURN r' % (owner.username, current_time, current_time)
        db.cypher_query(query)
        cache.set("%s_quest" % quest.object_uuid, quest)
        cache.delete(owner.username)
        cache.set("%s_privileges" % owner.username,
                  owner.get_privileges(cache_buster=True))
        cache.set("%s_actions" % owner.username,
                  owner.get_actions(cache_buster=True))
        spawn_task(task_func=check_privileges,
                   task_param={"username": owner.username})
        return quest

    def update(self, instance, validated_data):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_token = validated_data.pop('stripe_token', None)
        promotion_key = validated_data.pop('promotion_key', None)
        customer_token = validated_data.pop('customer_token',
                                            instance.customer_token)
        account_type = validated_data.get(
            'account_type', instance.account_type)
        instance.stripe_account_type = validated_data.get(
            'stripe_account_type', instance.stripe_account_type)
        instance.account_owner = validated_data.get('account_owner',
                                                    instance.account_owner)
        initial_state = instance.active
        customer = None
        ein = validated_data.pop('ein', instance.ein)
        ssn = validated_data.pop('ssn', instance.ssn)

        # ** Standard Settings Update **
        # Remove any dashes from the ssn input.
        if ssn is not None:
            ssn = ssn.replace('-', "")
        active = validated_data.pop('active', instance.active)
        instance.active = active
        instance.title = empty_text_to_none(
            validated_data.pop('title', instance.title))
        instance.facebook = clean_url(
            validated_data.get('facebook', instance.facebook))
        instance.linkedin = clean_url(
            validated_data.get('linkedin', instance.linkedin))
        instance.youtube = clean_url(
            validated_data.get('youtube', instance.youtube))
        instance.twitter = clean_url(
            validated_data.get('twitter', instance.twitter))
        if initial_state is True and active is False:
            remove_search_object(instance.object_uuid, "quest")
        instance.website = clean_url(validated_data.get(
            'website', instance.website))
        instance.about = empty_text_to_none(
            validated_data.get('about', instance.about))
        instance.wallpaper_pic = validated_data.get('wallpaper_pic',
                                                    instance.wallpaper_pic)
        instance.profile_pic = validated_data.get('profile_pic',
                                                  instance.profile_pic)
        owner = Pleb.get(username=instance.owner_username)

        # ** Customer Creation/Card Assignment If Provided **
        if customer_token is not None:
            # Customers must provide a credit card for us to create a customer
            # with stripe. Get the credit card # and create a customer instance
            # so we can charge it in the future.
            if instance.stripe_customer_id is None:
                customer = stripe.Customer.create(
                    description="Customer for %s Quest" % instance.object_uuid,
                    card=customer_token,
                    email=owner.email
                )
                instance.stripe_customer_id = customer['id']
                instance.stripe_default_card_id = customer[
                    'sources']['data'][0]['id']
            else:
                customer = stripe.Customer.retrieve(
                    instance.stripe_customer_id)
                card = customer.sources.create(source=customer_token)
                instance.stripe_default_card_id = card['id']
        elif customer_token is None and account_type == "promotion":
            if instance.stripe_customer_id is None:
                customer = stripe.Customer.create(
                    description="Customer for %s Quest" % instance.object_uuid,
                    email=owner.email)
                instance.stripe_customer_id = customer['id']

        # ** Account plan updating process **
        if account_type != instance.account_type:
            if customer is None:
                customer = stripe.Customer.retrieve(instance.stripe_customer_id)
            if account_type == "paid":
                # if paid gets submitted create a subscription if it doesn't
                # already exist
                if instance.stripe_subscription_id is None:
                    sub = customer.subscriptions.create(plan='quest_premium')
                    instance.stripe_subscription_id = sub['id']
                instance.application_fee = settings.STRIPE_PAID_ACCOUNT_FEE
            elif account_type == "promotion":
                if promotion_key in settings.PROMOTION_KEYS \
                        and settings.PRO_QUEST_PROMOTION:
                    if datetime.now() < settings.PRO_QUEST_END_DATE:
                        next_year = datetime.now() + relativedelta(years=+1)
                        unix_stamp = time.mktime(next_year.timetuple())
                        # Only allow people without subscriptions to create
                        # a new one with a trial.
                        # TODO for existing customers we need to create
                        # coupons through Stripe so that we don't have
                        # duplicate subscriptions associated with one
                        # user.
                        if instance.stripe_subscription_id is None:
                            sub = customer.subscriptions.create(
                                plan='quest_premium',
                                trial_end=int(unix_stamp))
                            instance.stripe_subscription_id = sub['id']
                            instance.application_fee = \
                                settings.STRIPE_PAID_ACCOUNT_FEE
                    else:
                        account_type = instance.account_type
                else:
                    account_type = instance.account_type
            elif account_type == "free":
                # if we get a free submission and the subscription is already
                # set cancel it.
                if instance.stripe_subscription_id is not None:
                    customer.subscriptions.retrieve(
                        instance.stripe_subscription_id).delete()
                    instance.stripe_subscription_id = None
                instance.application_fee = settings.STRIPE_FREE_ACCOUNT_FEE

            instance.account_type = account_type

        # ** Managed Account Setup **
        if stripe_token is not None:
            if instance.stripe_id is None or instance.stripe_id == "Not Set":
                account = stripe.Account.create(managed=True, country="US",
                                                email=owner.email)
                instance.stripe_id = account['id']
            else:
                account = stripe.Account.retrieve(instance.stripe_id)

            try:
                account.external_accounts.create(external_account=stripe_token)
            except InvalidRequestError:
                raise serializers.ValidationError(
                    detail={"detail": "Looks like we're having server "
                                      "issus, please contact us using the "
                                      "bubble in the bottom right",
                            "status_code": status.HTTP_400_BAD_REQUEST})
            owner_address = owner.get_address()
            if not instance.tos_acceptance:
                request = self.context.get('request', None)
                if request is not None:
                    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                    if x_forwarded_for:
                        ip = x_forwarded_for.split(',')[0]
                    else:
                        ip = request.META.get('REMOTE_ADDR')
                    account.tos_acceptance.ip = ip
                    account.tos_acceptance.date = int(time.time())
                    instance.account_verified_date = datetime.now(pytz.utc)
                    instance.tos_acceptance = True
            account.legal_entity.additional_owners = []
            account.legal_entity.personal_id_number = ssn
            if ein:
                account.legal_entity.business_tax_id = ein
            account.legal_entity.first_name = owner.first_name
            account.legal_entity.last_name = owner.last_name
            if instance.account_owner != "" \
                    and instance.account_owner is not None:
                account.business_name = instance.account_owner
                account.legal_entity.business_name = instance.account_owner
            stripe_account_type = instance.stripe_account_type
            if stripe_account_type == "business":
                stripe_account_type = 'company'
            account.legal_entity.type = stripe_account_type
            account.legal_entity.dob = dict(
                day=owner.date_of_birth.day,
                month=owner.date_of_birth.month,
                year=owner.date_of_birth.year
            )
            street_additional = empty_text_to_none(
                owner_address.street_additional)

            account.legal_entity.address.line1 = owner_address.street
            account.legal_entity.address.line2 = street_additional
            account.legal_entity.address.city = owner_address.city
            account.legal_entity.address.state = owner_address.state
            account.legal_entity.address.postal_code = \
                owner_address.postal_code
            account.legal_entity.address.country = "US"
            account.legal_entity.personal_address.line1 = owner_address.street
            account.legal_entity.personal_address.line2 = street_additional
            account.legal_entity.personal_address.city = owner_address.city
            account.legal_entity.personal_address.state = owner_address.state
            account.legal_entity.personal_address.postal_code = \
                owner_address.postal_code
            account.legal_entity.personal_address.country = \
                owner_address.country
            account = account.save()
            # Default to pending to make sure customer doesn't think nothing
            # is happening on a slow update from Stripe. We can revert back
            # to unverified if Stripe alerts us to it.
            verification = "pending"
            if account['legal_entity']['verification']['status'] == "verified":
                verification = account['legal_entity'][
                    'verification']['status']
            instance.account_verified = verification
            instance.last_four_soc = ssn[-4:]
        instance.save()
        cache.delete("%s_quest" % instance.owner_username)

        # ** Search Update **
        if instance.active:
            return super(QuestSerializer, self).update(instance, validated_data)
        return instance

    def get_url(self, obj):
        if obj.owner_username is not None and obj.owner_username != "":
            # We need a try catch here as there are some campaigns that have
            # username set but may not have a Pleb. This is only seen in tests
            # and has not been observed in production.
            username = obj.owner_username
        else:
            username = obj.object_uuid
        return reverse('quest', kwargs={"username": username},
                       request=self.context.get('request', None))

    def get_href(self, obj):
        return reverse('quest-detail',
                       kwargs={'owner_username': obj.owner_username},
                       request=self.context.get('request', None))

    def get_updates(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        updates = Quest.get_updates(obj.object_uuid)
        if relation == 'hyperlink':
            return [reverse('update-detail',
                            kwargs={'object_uuid': update},
                            request=request) for update in updates]
        return updates

    def get_completed_stripe(self, obj):
        # Whether or not stripe has verified the account information and
        # the Quest can start accepting donations.
        if obj.stripe_id == "Not Set":
            return False
        return True

    def get_is_editor(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        if request is None:
            return None
        return request.user.username in Quest.get_editors(obj.object_uuid)

    def get_is_moderator(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        if request is None:
            return None
        return request.user.username in Quest.get_moderators(obj.object_uuid)

    def get_completed_customer(self, obj):
        if obj.stripe_customer_id is None:
            return False
        return True

    def get_missions(self, obj):
        from sb_missions.neo_models import Mission
        from sb_missions.serializers import MissionSerializer
        expand = self.context.get('expand', 'false').lower()
        query = 'MATCH (quest:Quest {owner_username: "%s"})-[:EMBARKS_ON]->' \
                '(mission:Mission) RETURN mission' % obj.owner_username
        res, _ = db.cypher_query(query)
        if res.one is None:
            return None
        if expand == 'true':
            return [MissionSerializer(Mission.inflate(row[0])).data
                    for row in res]
        return [reverse('mission-detail',
                        kwargs={
                            'object_uuid': Mission.inflate(row[0]).object_uuid
                        }, request=self.context.get('request', None))
                for row in res]

    def get_total_donation_amount(self, obj):
        return obj.get_total_donation_amount()

    def get_is_following(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        if request is None:
            return None
        return obj.is_following(request.user.username)


class EditorSerializer(serializers.Serializer):
    # profiles is expected to be a list of pleb usernames, not the entire pleb
    # object
    profiles = serializers.ListField(
        child=serializers.CharField(max_length=36)
    )

    def update(self, instance, validated_data):
        """
        The instance passed here much be a Campaign or any subclass of a
        Campaign
        :param instance:
        :param validated_data:
        :return:
        """
        current_editors = cache.get("%s_editors" % instance.object_uuid, [])
        for profile in \
                list(set(validated_data['profiles']) - set(current_editors)):
            profile_pleb = Pleb.get(username=profile)
            instance.editors.connect(profile_pleb)
        cache.delete("%s_editors" % instance.owner_username)
        return instance

    def remove_profiles(self, instance):
        for profile in self.data['profiles']:
            profile_pleb = Pleb.get(username=profile)
            instance.editors.disconnect(profile_pleb)
        cache.delete("%s_editors" % instance.owner_username)
        return instance


class ModeratorSerializer(serializers.Serializer):
    # profiles is expected to be a list of pleb usernames, not the entire pleb
    # object
    profiles = serializers.ListField(
        child=serializers.CharField(max_length=36)
    )

    def update(self, instance, validated_data):
        current_moderators = cache.get("%s_moderators" %
                                       instance.owner_username, [])
        for profile in \
                list(set(validated_data['profiles']) - set(
                     current_moderators)):
            profile_pleb = Pleb.get(username=profile)
            instance.moderators.connect(profile_pleb)
        cache.delete("%s_moderators" % instance.owner_username)
        return instance

    def remove_profiles(self, instance):
        for profile in self.data['profiles']:
            profile_pleb = Pleb.get(username=profile)
            instance.moderators.disconnect(profile_pleb)
        cache.delete("%s_moderators" % instance.owner_username)
        return instance


class AccountantSerializer(serializers.Serializer):
    # profiles is expected to be a list of pleb usernames, not the entire pleb
    # object
    profiles = serializers.ListField(
        child=serializers.CharField(max_length=30)
    )

    def update(self, instance, validated_data):
        current_accountants = cache.get("%s_accountants" %
                                        instance.object_uuid, [])
        for profile in \
                list(set(validated_data['profiles']) - set(
                     current_accountants)):
            profile_pleb = Pleb.get(username=profile)
            instance.accountants.connect(profile_pleb)
            profile_pleb.campaign_accountant.connect(instance)
        cache.delete("%s_accountants" % instance.object_uuid)
        return instance

    def remove_profiles(self, instance):
        for profile in self.data['profiles']:
            profile_pleb = Pleb.get(username=profile)
            instance.accountants.disconnect(profile_pleb)
            profile_pleb.campaign_accountant.disconnect(instance)
        cache.delete("%s_accountants" % instance.object_uuid)
        return instance


class PositionSerializer(SBSerializer):
    name = serializers.CharField()
    full_name = serializers.CharField()
    verified = serializers.BooleanField()
    user_created = serializers.BooleanField()
    office_type = serializers.ChoiceField(
        required=False, allow_blank=True, choices=[
            ('executive', "Executive"), ('legislative', "Legislative"),
            ('judicial', "Judicial"), ('enforcement', 'Enforcement')]
    )
    level = serializers.CharField()
    href = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    location_name = serializers.SerializerMethodField()

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.verified = validated_data.get('verified', instance.verified)
        instance.level = validated_data.get('level', instance.level)
        office_type = validated_data.get('office_type', instance.office_type)
        if office_type:
            instance.office_type = validated_data.get('office_type',
                                                      instance.office_type)
        instance.save()
        cache.delete(instance.object_uuid)
        return instance

    def get_href(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return reverse('position-detail',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=request)

    def get_location(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        location = Position.get_location(obj.object_uuid)
        if relation == 'hyperlink':
            return reverse('location-detail',
                           kwargs={'object_uuid': location},
                           request=request)
        return location

    def get_location_name(self, obj):
        return Position.get_location_name(obj.object_uuid)


class PositionManagerSerializer(SBSerializer):
    name = serializers.CharField()
    level = serializers.ChoiceField(required=True, choices=[
        ('local', "Local"), ('state', "State"),
        ('federal', "Federal")])
    location_name = serializers.CharField(allow_blank=True)
    location_uuid = serializers.CharField(allow_blank=True)

    def create(self, validated_data):
        location = None
        location_name = validated_data.pop('location_name', '')
        location_id = validated_data.pop('location_uuid', '')
        try:
            location = Location.nodes.get(name=location_name)
        except(Location.DoesNotExist, DoesNotExist):
            pass
        if location is None:
            try:
                location = Location.nodes.get(object_uuid=location_id)
            except(Location.DoesNotExist, DoesNotExist):
                pass
        position = Position(**validated_data).save()
        if location is not None:
            position.location.connect(location)
        position.full_name = Position.get_full_name(position.object_uuid)
        position.save()
        return position
