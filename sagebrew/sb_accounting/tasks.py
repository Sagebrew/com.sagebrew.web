import pytz
import calendar
from datetime import datetime
from celery import shared_task
from intercom import Event, Intercom, errors

from neomodel import db

from sb_quests.neo_models import Quest

from logging import getLogger
logger = getLogger('loggly_logs')


@shared_task()
def check_unverified_quest():
    # TODO replace these with environmental variables
    Intercom.app_id = "jmz4pnau"
    Intercom.app_api_key = "24a76d234536a2115ebe4b4e8bfe3ed8aaaa6884"
    now = datetime.now(pytz.utc)
    query = 'MATCH (q:Quest) WHERE q.account_verified<>"verified" ' \
            'AND q.account_first_updated IS NOT NULL RETURN q'
    res, _ = db.cypher_query(query)
    for row in res:
        quest = Quest.inflate(row[0])
        if (now - quest.account_first_updated).days >= 1:
            try:
                Event.create(event_name="still-unverified-quest",
                             user_id=quest.owner_username,
                             created=calendar.timegm(now.utctimetuple()))
            except errors.ResourceNotFound:
                continue
    logger.critical("Scheduled unverified Quest task ran!")
    return True
