from celery import shared_task

from api.utils import get_object

@shared_task()
def edit_object_task(object_uuid, object_type, current_pleb, content,
                     question_title=None):
    '''
    Question title is only used when editing a question.
    :param object_uuid:
    :param object_type:
    :param current_pleb:
    :param content:
    :param question_title:
    :return:
    '''
    sb_object = get_object(object_type, object_uuid)
    if isinstance(sb_object, Exception) is True:
        raise edit_object_task.retry(exc=sb_object, countdown=3,
                                     max_retries=None)
    res = sb_object.edit_content(content=content, pleb=current_pleb,
                                 question_title=question_title)

    if isinstance(res, Exception) is True:
        raise edit_object_task.retry(exc=res, countdown=3, max_retries=None)
    else:
        return res