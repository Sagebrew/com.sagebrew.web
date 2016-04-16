import time

from django.conf import settings

from celery import shared_task

from intercom import (Message, Event, Intercom, ResourceNotFound,
                      UnexpectedError, RateLimitExceeded, ServerError,
                      ServiceUnavailableError, BadGatewayError, HttpError)


@shared_task()
def create_email(message_data):
    Intercom.app_id = settings.INTERCOM_APP_ID
    Intercom.app_api_key = settings.INTERCOM_API_KEY
    try:
        Message.create(**message_data)
    except (ResourceNotFound, UnexpectedError) as e:
        raise create_email.retry(exc=e, countdown=10, max_retries=None)
    except (RateLimitExceeded, ServerError, ServiceUnavailableError,
            BadGatewayError, HttpError) as e:
        raise create_email.retry(exc=e, countdown=120, max_retries=None)


@shared_task()
def create_event(event_name, username, metadata=None):
    if metadata is None:
        metadata = {}
    Intercom.app_id = settings.INTERCOM_APP_ID
    Intercom.app_api_key = settings.INTERCOM_API_KEY
    try:
        Event.create(
            event_name=event_name,
            created_at=int(time.time()),
            user_id=username,
            metadata=metadata)
    except (ResourceNotFound, UnexpectedError) as e:
        raise create_event.retry(exc=e, countdown=10, max_retries=None)
    except (RateLimitExceeded, ServerError, ServiceUnavailableError,
            BadGatewayError, HttpError) as e:
        raise create_event.retry(exc=e, countdown=10, max_retries=None)
