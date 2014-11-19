import logging
from celery import shared_task

from api.utils import get_object
from sb_base.utils import defensive_exception

logger = logging.getLogger("loggly_logs")


@shared_task()
def delete_object_task(object_type, object_uuid, current_pleb):
    try:
        sb_object = get_object(object_type, object_uuid)
        if isinstance(sb_object, Exception) is True:
            raise delete_object_task.retry(exc=sb_object, countdown=3,
                                           max_retries=None)
        elif sb_object is False:
            return sb_object

        res = sb_object.delete_content(current_pleb)

        if isinstance(res, Exception) is True:
            raise delete_object_task.retry(exc=res, countdown=3, max_retries=None)
        else:
            return res
    except Exception as e:
        raise defensive_exception(delete_object_task.__name__, e,
                                  delete_object_task.retry(exc=e,
                                                           countdown=3,
                                                           max_retries=None))