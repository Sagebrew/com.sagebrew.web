from logging import getLogger
import pytz
import stripe
import calendar
from uuid import uuid1
from datetime import datetime
from intercom import Intercom, Event

from sb_base.serializers import IntercomMessageSerializer

from sb_quests.neo_models import Quest
from sb_notifications.tasks import spawn_system_notification
from django.conf import settings
from django.core.cache import cache

from rest_framework import serializers
from rest_framework.reverse import reverse

from api.utils import spawn_task
from api.serializers import SBSerializer
from plebs.neo_models import Pleb

logger = getLogger("loggly_logs")


class AccountSerializer(SBSerializer):
    id = serializers.CharField(max_length=256)
    detail = serializers.CharField(required=False, allow_null=True,
                                   allow_blank=True)

    def create(self, validated_data):
        logger.critical(validated_data)
        logger.critical("we're receiving info!")
        Intercom.app_id = settings.INTERCOM_APP_ID
        Intercom.app_api_key = settings.INTERCOM_API_KEY
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            event = stripe.Event.retrieve(validated_data['id'])
        except stripe.InvalidRequestError:
            raise serializers.ValidationError('Please provide a valid id')

        if event.type == "invoice.payment_failed":
            try:
                customer = stripe.Customer.retrieve(
                    event.data.object.customer)
            except stripe.InvalidRequestError as e:
                return serializers.ValidationError(e)
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
            return {"detail": "Invoice Payment Failed",
                    "id": validated_data['id']}
        if event.type == "account.updated":
            try:
                account = stripe.Account.retrieve(
                    event.data.object.id
                )
            except (stripe.InvalidRequestError, stripe.APIConnectionError) as e:
                raise serializers.ValidationError(e)
            pleb = Pleb.nodes.get(email=account.email)
            quest = Quest.nodes.get(owner_username=pleb.username)
            if account.verification.fields_needed:
                quest.account_verification_fields_needed = \
                    account.verification.fields_needed

            if quest.account_verified != "verified" \
                    and account.legal_entity.verification.status == "verified":
                spawn_task(
                    task_func=spawn_system_notification,
                    task_param={
                        "to_plebs": [pleb.username],
                        "notification_id": str(uuid1()),
                        "url": reverse('quest_manage_banking',
                                       kwargs={'username': pleb.username}),
                        "action_name": "Your Quest has been verified!"
                    }
                )
                quest.active = True
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
            return {"detail": "Account Updated",
                    "id": validated_data['id']}
        if event.type == "transfer.failed":
            try:
                transfer = stripe.Transfer.retrieve(
                    event.data.object.id
                )
                if transfer.type == 'stripe_account':
                    account = stripe.Account.retrieve(
                        transfer.destination
                    )
                else:
                    raise serializers.ValidationError('An error occurred')
            except (stripe.InvalidRequestError, stripe.APIConnectionError) as e:
                raise serializers.ValidationError(e)
            pleb = Pleb.nodes.get(email=account.email)
            spawn_task(
                task_func=spawn_system_notification,
                task_param={
                    "to_plebs": [pleb.username],
                    "notification_id": str(uuid1()),
                    "url": reverse('quest_manage_banking',
                                   kwargs={"username": pleb.username}),
                    "action_name": "A transfer to your bank account has "
                                   "failed! Please review that your "
                                   "Quest Banking information is correct."
                }
            )
            Event.create(event_name="stripe-transfer-failed",
                         user_id=pleb.username,
                         created=calendar.timegm(
                             datetime.now(pytz.utc).utctimetuple()))
            return {"detail": "Transfer Failed", "id": validated_data['id']}
        if event.type == 'customer.subscription.trial_will_end':
            try:
                customer = stripe.Customer.retrieve(
                    event.data.object.customer
                )
            except (stripe.InvalidRequestError, stripe.APIConnectionError) as e:
                raise serializers.ValidationError(e)
            pleb = Pleb.nodes.get(email=customer.email)
            spawn_task(
                task_func=spawn_system_notification,
                task_param={
                    "to_plebs": [pleb.username],
                    "notification_id": str(uuid1()),
                    "url": reverse('quest_manage_billing',
                                   kwargs={"username": pleb.username}),
                    "action_name": "Your Pro Trial will "
                                   "be ending soon, add a payment method to "
                                   "keep your Pro Account features."
                }
            )
            return {"detail": "Trail Will End", "id": validated_data['id']}
        return {"detail": "No updates", "id": validated_data['id']}
