import stripe

from django.conf import settings
from django.core.management.base import BaseCommand

from logging import getLogger
logger = getLogger("loggly_logs")


class Command(BaseCommand):
    args = 'None.'

    def create_subscription_plans(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            stripe.Plan.create(
                amount=10000,
                interval='month',
                name='Sagebrew Premium Quest Account',
                currency='usd',
                id='quest_premium'
            )
        except stripe.InvalidRequestError:
            # pass here if we get this error because it just means the
            # plan already exists in stripe
            pass

    def handle(self, *args, **options):
        self.create_subscription_plans()
