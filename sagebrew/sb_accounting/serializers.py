from logging import getLogger
import pytz
import stripe
import calendar
from uuid import uuid1
from datetime import datetime
from intercom import Intercom, Event

from django.conf import settings
from django.core.cache import cache

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import db

from api.serializers import SBSerializer
from sb_base.serializers import IntercomMessageSerializer
from sb_notifications.utils import create_system_notification
from plebs.neo_models import Pleb
from sb_quests.serializers import QuestSerializer
from sb_quests.neo_models import Quest

logger = getLogger("loggly_logs")


class AccountSerializer(SBSerializer):
    id = serializers.CharField(max_length=256)
    type = serializers.CharField(max_length=256)
    data = serializers.DictField()
    detail = serializers.CharField(required=False, allow_null=True,
                                   allow_blank=True)

    def create(self, validated_data):
        request = self.context.get('request')
        response_dict = {
            "id": validated_data['id'],
            "type": validated_data['type'], 'data': validated_data['data']
        }
        Intercom.app_id = settings.INTERCOM_APP_ID
        Intercom.app_api_key = settings.INTERCOM_API_KEY
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = settings.STRIPE_API_VERSION
        event_type = validated_data['type']
        if event_type == "invoice.payment_failed":
            try:
                customer = stripe.Customer.retrieve(
                    validated_data['data']['object']['customer'])
            except stripe.InvalidRequestError:
                raise serializers.ValidationError("Ran into some issues")
            pleb = Pleb.nodes.get(email=customer['email'])

            message_data = {
                'message_type': 'email',
                'subject': 'Subscription Failure Notice',
                'body': "Hi {{ first_name }},\nIt looks like we ran into "
                        "some trouble processing your subscription payment. "
                        "Please verify your billing information is correct "
                        "and we'll automatically retry to process the payment. "
                        "If the payment continues to fail we'll automatically "
                        "move you over to a free account. If you believe "
                        "there has been a mistake please respond to this "
                        "email and we'd be happy to help!\n\nBest Regards,"
                        "\n\nDevon",
                'template': 'personal',
                'from_user': {
                    'type': 'admin',
                    'id': settings.INTERCOM_ADMIN_ID_DEVON
                },
                'to_user': {
                    'type': 'user',
                    'user_id': pleb.username
                }
            }
            serializer = IntercomMessageSerializer(data=message_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response_dict["detail"] = "Invoice Payment Failed"
            return response_dict
        if event_type == "account.updated":
            try:
                account = stripe.Account.retrieve(
                    validated_data['data']['object']['id']
                )
            except (stripe.InvalidRequestError, stripe.APIConnectionError) as e:
                logger.exception(e)
                raise serializers.ValidationError(e)
            pleb = Pleb.nodes.get(email=account.email)
            quest = Quest.nodes.get(owner_username=pleb.username)

            if quest.account_verified != "verified" \
                    and account.legal_entity.verification.status == "verified":
                # Need this to ensure the notification is only sent once if
                # Stripe sends a subsequent message before we've saved the
                # verification off.
                query = 'MATCH (a:Notification {action_name: ' \
                        '"Your Quest has been verified!"})' \
                        '-[:NOTIFICATION_TO]->(pleb:Pleb {username: "%s"}) ' \
                        'RETURN a' % pleb.username
                res, _ = db.cypher_query(query)
                if res.one is None:
                    create_system_notification(
                        to_plebs=[pleb],
                        notification_id=str(uuid1()),
                        url=reverse('quest_manage_banking',
                                    kwargs={'username': pleb.username}),
                        action_name="Your Quest has been verified!"
                    )
                quest_ser = QuestSerializer(
                    instance=quest, data={'active': True},
                    context={"secret": settings.SECRET_KEY,
                             "request": request})
                quest_ser.is_valid(raise_exception=True)
                quest_ser.save()
                cache.delete("%s_quest" % quest.owner_username)
                # Update quest after saving from serializer so we're not working
                # with a stale instance.
                quest = Quest.nodes.get(owner_username=pleb.username)
                quest.account_verified_date = datetime.now(pytz.utc)
            if account.verification.fields_needed:
                quest.account_verification_fields_needed = \
                    account.verification.fields_needed
            quest.account_verified = \
                account.legal_entity.verification.status
            quest.account_verification_details = \
                str(account.legal_entity.verification.details)
            if quest.account_first_updated is None \
                    and quest.account_verified != "verified":
                quest.account_first_updated = datetime.now(pytz.utc)
            verify = account.verification

            # Determine if we need Quest to upload identification documentation
            if 'legal_entity.verification.document' in verify.fields_needed:
                quest.verification_document_needed = True

            # Save off when the additional information is due by
            if hasattr(verify, 'due_by') and verify.due_by is not None:
                quest.verification_due_date = datetime.datetime.fromtimestamp(
                    account.verification.due_by)
            else:
                quest.verification_due_date = None

            # Indicate why the account was disabled by the payment processing
            # platform
            if verify.disabled_reason is not None:
                quest.verification_disabled_reason = \
                    account.verification.disabled_reason\
                    .replace('_', " ").title()
            else:
                quest.verification_disabled_reason = None

            quest.save()
            cache.delete("%s_quest" % quest.owner_username)
            response_dict["detail"] = "Account Updated"
            return response_dict
        if event_type == "transfer.failed":
            try:
                transfer = stripe.Transfer.retrieve(
                    validated_data['data']['object']['id']
                )
                if transfer.type == 'stripe_account':
                    account = stripe.Account.retrieve(
                        transfer.destination
                    )
                else:
                    raise serializers.ValidationError('An error occurred')
            except (stripe.InvalidRequestError, stripe.APIConnectionError) as e:
                logger.exception(e)
                raise serializers.ValidationError(e)
            pleb = Pleb.nodes.get(email=account.email)
            create_system_notification(
                to_plebs=[pleb],
                notification_id=str(uuid1()),
                url=reverse('quest_manage_banking',
                            kwargs={'username': pleb.username}),
                action_name="A transfer to your bank account has "
                            "failed! Please review that your "
                            "Quest Banking information is correct."
            )
            Event.create(event_name="stripe-transfer-failed",
                         user_id=pleb.username,
                         created=calendar.timegm(
                             datetime.now(pytz.utc).utctimetuple()))
            response_dict["detail"] = "Transfer Failed"
            return response_dict
        if event_type == 'customer.subscription.trial_will_end':
            try:
                customer = stripe.Customer.retrieve(
                    validated_data['data']['object']['customer']
                )
            except (stripe.InvalidRequestError, stripe.APIConnectionError) as e:
                logger.exception(e)
                raise serializers.ValidationError(e)
            pleb = Pleb.nodes.get(email=customer.email)
            create_system_notification(
                to_plebs=[pleb],
                notification_id=str(uuid1()),
                url=reverse('quest_manage_billing',
                            kwargs={'username': pleb.username}),
                action_name="Your Pro Trial will "
                            "be ending soon, add a payment method to "
                            "keep your Pro Account features."
            )
            response_dict["detail"] = "Trail Will End"
            return response_dict
        response_dict["detail"] = "No updates"
        return response_dict
