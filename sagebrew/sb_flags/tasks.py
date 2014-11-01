from celery import shared_task

from .utils import flag_object_util

@shared_task()
def flag_object_task(current_pleb, sb_object, flag_reason):
    '''
    This function takes a pleb object,
    sb_object(SBAnswer, SBQuestion, SBComment, SBPost), and a flag reason.
    It will then call a util to create the flag and add it to the object.

    :param current_pleb:
    :param sb_object:
    :param flag_reason:
    :return:
    '''
    res = flag_object_util(current_pleb=current_pleb, sb_object=sb_object,
                           flag_reason=flag_reason)
    if res is True:
        return True
    elif type(res) is type(Exception):
        raise flag_object_task.retry(exc=res, countdown=3, )
    pass