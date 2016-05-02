from logging import getLogger
from datetime import datetime, timedelta
import stripe
import json
import requests

from django.conf import settings

from rest_framework.reverse import reverse

logger = getLogger('loggly_logs')


def get_events(request):
    try:
        if not settings.DEBUG:
            return None
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = settings.STRIPE_API_VERSION
        for event in stripe.Event.all(
                limit=10,
                created={'gte': (datetime.utcnow() -
                                 timedelta(minutes=10)).strftime("%s")}).data:
            logger.critical(event.id)
            response = requests.post(
                url=reverse('accounting-list', request=request),
                data=json.dumps({"id": event.id}),
                headers={"content-type": "application/json"},
                verify=False)
            logger.critical(response.json())
            logger.critical(response.status_code)
    except Exception as e:
        logger.exception(e)

    return True
