from celery import shared_task

from api.utils import get_object
from .utils import vote_object_util


@shared_task()
def vote_object_task(vote_type, current_pleb, object_type, object_uuid):
    '''
    This function takes a pleb object, an
    sb_object(SBAnswer, SBQuestion, SBComment, SBPost), and a
    vote_type("up", "down") it will then call a util to hanlde the vote
    operations on the sb_object.

    :param vote_type:
    :param current_pleb:
    :param sb_object:
    :return:
    '''
    sb_object = get_object(object_type, object_uuid)
    if isinstance(sb_object, Exception) is True:
        raise vote_object_task.retry(exc=sb_object, countdown=3,
                                     max_retries=None)
    res = sb_object.vote_content(vote_type, current_pleb)

    if isinstance(res, Exception) is True:
        raise vote_object_task.retry(exc=res, countdown=3, max_retries=None)
    else:
        return res
