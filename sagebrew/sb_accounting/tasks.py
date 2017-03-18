import pytz
import calendar
from datetime import datetime
from celery import shared_task

from neomodel import db

from sagebrew.sb_base.serializers import IntercomEventSerializer

from logging import getLogger
logger = getLogger('loggly_logs')


@shared_task()
def check_unverified_quest():
    now = datetime.now(pytz.utc)
    query = 'MATCH (q:Quest) WHERE q.account_verified<>"verified" ' \
            'AND q.account_first_updated IS NOT NULL AND ' \
            '%d-q.account_first_updated >= 86400 RETURN ' \
            'q.owner_username as username' % \
            (calendar.timegm(now.utctimetuple()))
    res, _ = db.cypher_query(query)
    for row in res:
        data = {
            "event_name": "still-unverified-quest",
            "username": row.username
        }
        serializer = IntercomEventSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
    logger.critical("Scheduled unverified Quest task ran!")
    return True
