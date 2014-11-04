from celery import shared_task

from api.utils import get_object
from .utils import flag_object_util

@shared_task()
def flag_object_task(current_pleb, object_uuid, object_type, flag_reason):
    '''
    This function takes a pleb object,
    sb_object(SBAnswer, SBQuestion, SBComment, SBPost), and a flag reason.
    It will then call a util to create the flag and add it to the object.

    :param current_pleb:
    :param sb_object:
    :param flag_reason:
    :return:
    '''
    sb_object = get_object(object_type, object_uuid)
    if isinstance(sb_object, Exception) is True:
        raise flag_object_task.retry(exc=sb_object, countdown=3,
                                     max_retries=None)
    res = flag_object_util(current_pleb=current_pleb, sb_object=sb_object,
                           flag_reason=flag_reason)
    if isinstance(res, Exception) is True:
        raise flag_object_task.retry(exc=res, countdown=3, max_retries=None)
    else:
        return res