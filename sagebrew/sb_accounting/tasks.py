import pytz
import calendar
from datetime import datetime
from celery import shared_task
from intercom import Event, Intercom, errors

from sb_quests.neo_models import Quest

from logging import getLogger
logger = getLogger('loggly_logs')


@shared_task()
def check_unverified_quest():
    # TODO replace these with environmental variables
    Intercom.app_id = "jmz4pnau"
    Intercom.app_api_key = "24a76d234536a2115ebe4b4e8bfe3ed8aaaa6884"
    now = datetime.now(pytz.utc)
    for quest in Quest.nodes.all():
        if quest.account_verified != "verified" \
                and quest.account_first_updated is not None:
            if (now - quest.account_first_updated).days >= 3:
                try:
                    Event.create(event_name="still-unverified-quest",
                                 user_id=quest.owner_username,
                                 created=calendar.timegm(now.utctimetuple()))
                    quest.account_first_updated = None
                    quest.save()
                except errors.ResourceNotFound:
                    continue
    logger.critical("Scheduled unverified Quest task ran!")
    return True
