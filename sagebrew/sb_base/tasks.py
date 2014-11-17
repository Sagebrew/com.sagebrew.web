import logging
from json import dumps
from celery import shared_task

from sb_base.utils import defensive_exception

logger = logging.getLogger("loggly_logs")


@shared_task()
def create_object_relations_task(sb_object, current_pleb, question=None,
                                 wall=None):
    try:
        res = sb_object.create_relations(current_pleb, question, wall)
        if isinstance(res, Exception) is True:
            raise create_object_relations_task.retry(exc=res, countdown=3,
                                                     max_retries=None)
        return True
    except Exception as e:
        raise defensive_exception(create_object_relations_task.__name__, e,
                                  create_object_relations_task.retry(
                                      exc=e, countdown=3, max_retries=None))
