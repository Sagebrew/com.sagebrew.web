import pytz
import calendar
from datetime import datetime
from celery import shared_task
from intercom import Event, Intercom, errors

from django.conf import settings

from neomodel import db

from logging import getLogger
logger = getLogger('loggly_logs')


@shared_task()
def check_unverified_quest():
    Intercom.app_id = settings.INTERCOM_APP_ID
    Intercom.app_api_key = settings.INTERCOM_API_KEY
    now = datetime.now(pytz.utc)
    query = 'MATCH (q:Quest) WHERE q.account_verified<>"verified" ' \
            'AND q.account_first_updated IS NOT NULL AND ' \
            '%d-q.account_first_updated >= 86400 RETURN ' \
            'q.owner_username as username' % \
            (calendar.timegm(now.utctimetuple()))
    res, _ = db.cypher_query(query)
    for row in res:
        try:
            Event.create(event_name="still-unverified-quest",
                         user_id=row.username,
                         created=calendar.timegm(now.utctimetuple()))
        except errors.ResourceNotFound:
            continue
    logger.critical("Scheduled unverified Quest task ran!")
    return True
