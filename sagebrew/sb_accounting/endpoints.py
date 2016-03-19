import pytz
import stripe
import calendar
from uuid import uuid1
from datetime import datetime
from intercom import Intercom, Event, Message

from django.conf import settings

from rest_framework import status, viewsets
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication

from api.utils import spawn_task
from plebs.neo_models import Pleb
from sb_quests.neo_models import Quest
from sb_notifications.tasks import spawn_system_notification


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class AccountingViewSet(viewsets.ViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = ()

    def create(self, request):
        Intercom.app_id = settings.INTERCOM_APP_ID
        Intercom.app_api_key = settings.INTERCOM_API_KEY
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            event = stripe.Event.retrieve(request.data['id'])
        except stripe.InvalidRequestError:
            return Response(status=status.HTTP_200_OK)

        if event.type == "invoice.payment_failed":
            try:
                customer = stripe.Customer.retrieve(
                    event.data.object.customer)
            except stripe.InvalidRequestError:
                return Response(status=status.HTTP_200_OK)
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
                'from': {
                    'type': 'admin',
                    'id': settings.INTERCOM_ADMIN_ID_DEVON
                },
                'to': {
                    'type': 'user',
                    'id': pleb.username
                }
            }
            Message.create(**message_data)
            return Response({"detail": "Invoice Payment Failed"},
                            status=status.HTTP_200_OK)
        if event.type == "account.updated":
            try:
                account = stripe.Account.retrieve(
                    event.data.object.id
                )
            except stripe.InvalidRequestError:
                return Response(status=status.HTTP_200_OK)
            pleb = Pleb.nodes.get(email=account.email)
            quest = Quest.get(pleb.username)
            if account.verification.fields_needed:
                quest.account_verification_fields_needed = \
                    account.verification.fields_needed

            if quest.account_verified != "verified" \
                    and account.legal_entity.verification.status \
                    == "verified":
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
            quest.account_verified = \
                account.legal_entity.verification.status
            quest.account_verification_details = \
                str(account.legal_entity.verification.details)
            if quest.account_first_updated is None \
                    and quest.account_verified != "verified":
                quest.account_first_updated = datetime.now(pytz.utc)
            quest.save()
            return Response({"detail": "Account Updated"},
                            status=status.HTTP_200_OK)
        if event.type == "transfer.failed":
            try:
                transfer = stripe.Transfer.retrieve(
                    event.data.object.id
                )
                if transfer.type == 'stripe_account':
                    account = stripe.Account.retrieve(
                        transfer.destination
                    )
            except stripe.InvalidRequestError:
                return Response(status=status.HTTP_200_OK)
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
            return Response({"detail": "Transfer Failed"}, status.HTTP_200_OK)
        if event.type == 'customer.subscription.trial_will_end':
            try:
                customer = stripe.Customer.retrieve(
                    event.data.object.customer
                )
            except stripe.InvalidRequestError:
                return Response(status=status.HTTP_200_OK)
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
            return Response({"detail": "Trail Will End"},
                            status=status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK)
