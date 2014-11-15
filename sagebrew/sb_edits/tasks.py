import logging
from json import dumps
from celery import shared_task

from api.utils import get_object

logger = logging.getLogger('loggly_logs')


@shared_task()
def edit_object_task(object_uuid, object_type, current_pleb, content):
    '''
    :param object_uuid:
    :param object_type:
    :param current_pleb:
    :param content:
    :return:
    '''
    sb_object = get_object(object_type, object_uuid)
    if isinstance(sb_object, Exception) is True:
        raise edit_object_task.retry(exc=sb_object, countdown=3,
                                     max_retries=None)
    res = sb_object.edit_content(content=content, pleb=current_pleb)

    if isinstance(res, Exception) is True:
        raise edit_object_task.retry(exc=res, countdown=3, max_retries=None)
    else:
        return res

@shared_task()
def edit_question_task(object_uuid, object_type, current_pleb, question_title):
    sb_object = get_object(object_type, object_uuid)
    if isinstance(sb_object, Exception) is True:
        raise edit_question_task.retry(exc=sb_object, countdown=3,
                                       max_retries=None)

    res = sb_object.edit_title(pleb=current_pleb, title=question_title)

    if isinstance(res, Exception) is True:
        raise edit_question_task.retry(exc=res, countdown=3, max_retries=None)
    else:
        return res