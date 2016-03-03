import stripe

from django.conf import settings
from django.template.loader import render_to_string

from rest_framework import status, viewsets
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication

from api.utils import spawn_task
from plebs.neo_models import Pleb
from plebs.tasks import send_email_task


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class AccountingViewSet(viewsets.ViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = ()

    def create(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            event = stripe.Event.retrieve(request.data['id'])
        except stripe.InvalidRequestError:
            return Response(status=status.HTTP_200_OK)

        if event['type'] == "invoice.payment_failed":
            try:
                customer = stripe.Customer.retrieve(
                    event['data']['object']['customer'])
            except stripe.InvalidRequestError:
                return Response(status=status.HTTP_200_OK)
            pleb = Pleb.nodes.get(email=customer['email'])
            email_data = {
                "source": "support@sagebrew.com",
                "to": [pleb.email],
                "subject": "Subscription Failure Notice",
                "html_content": render_to_string(
                    "email_templates/email_subscription_failure_notice.html",
                    {"billing_url":
                        reverse("quest_manage_billing",
                                kwargs={'username': pleb.username})})
            }
            spawn_task(task_func=send_email_task, task_param=email_data)
            return Response({"detail": "Invoice Payment Failed"},
                            status=status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK)
