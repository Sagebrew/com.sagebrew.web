from celery import shared_task

from .utils import vote_object_util


@shared_task()
def vote_object_task(vote_type, current_pleb, sb_object):
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
    res = vote_object_util(vote_type=vote_type, current_pleb=current_pleb,
                           sb_object=sb_object)
    if res is True:
        return True
    elif isinstance(res, Exception) is True:
        raise vote_object_task.retry(exc=res, countdown=3, max_retries=None)
    else:
        return False
