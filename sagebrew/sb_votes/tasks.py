from celery import shared_task

from api.utils import get_object


@shared_task()
def vote_object_task(vote_type, current_pleb, object_type, object_uuid):
    '''
    This function takes a pleb object, an
    sb_object(SBSolution, SBQuestion, SBComment, SBPost), and a
    vote_type(True, False) it will then call a method to handle the vote
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
    elif sb_object is False:
        return sb_object

    res = sb_object.vote_content(vote_type, current_pleb)

    if isinstance(res, Exception) is True:
        raise vote_object_task.retry(exc=res, countdown=3, max_retries=None)

    res = sb_object.update_vote_count()

    if isinstance(res, Exception) is True:
        raise vote_object_task.retry(exc=res, countdown=3, max_retries=None)

    return sb_object
