import time

from django.conf import settings

from celery import shared_task

from intercom import (Message, Event, Intercom, ResourceNotFound,
                      UnexpectedError, RateLimitExceeded, ServerError,
                      ServiceUnavailableError, BadGatewayError, HttpError,
                      AuthenticationError)


@shared_task()
def create_email(message_data):
    Intercom.app_id = settings.INTERCOM_APP_ID
    Intercom.app_api_key = settings.INTERCOM_API_KEY
    try:
        Message.create(**message_data)
    except (ResourceNotFound, UnexpectedError) as e:
        raise create_email.retry(exc=e, countdown=10, max_retries=None)
    except RateLimitExceeded as e:
        # We don't want to continue bashing their API if we've
        # hit our limit. Intercom may then reduce our overall limit as
        # highlighted here
        # https://developers.intercom.io/reference#rate-limiting
        raise create_email.retry(exc=e, countdown=3600, max_retries=None)
    except (ServerError, ServiceUnavailableError,
            BadGatewayError, HttpError,
            AuthenticationError) as e:  # pragma: no cover
        # Not covering because Intercom does not have a good way of
        # simulating these conditions as of 04/16/2016  - Devon Bleibtrey
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
    except RateLimitExceeded as e:
        # We don't care too much about events getting spanned. They at least
        # don't affect the customer in a highly noticeable way. So if we've
        # exceeded our rate limit we can delay
        # But we def don't want to continue bashing their API if we've
        # hit our limit. Intercom may then reduce our overall limit as
        # highlighted here
        # https://developers.intercom.io/reference#rate-limiting
        raise create_email.retry(exc=e, countdown=86400, max_retries=None)
    except (ServerError, ServiceUnavailableError,
            BadGatewayError, HttpError,
            AuthenticationError) as e:  # pragma: no cover
        # Not covering because Intercom does not have a good way of
        # simulating these conditions as of 04/16/2016  - Devon Bleibtrey
        raise create_event.retry(exc=e, countdown=10, max_retries=None)
