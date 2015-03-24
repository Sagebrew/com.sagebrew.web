import logging

from celery import shared_task

from neomodel.exception import DoesNotExist, CypherException

from api.utils import get_object
from plebs.neo_models import Pleb

logger = logging.getLogger('loggly_logs')


@shared_task()
def edit_object_task(object_uuid, object_type, username, content):
    '''
    :param object_uuid:
    :param object_type:
    :param current_pleb:
    :param content:
    :return:
    '''
    try:
        current_pleb = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException, IOError) as e:
        raise edit_object_task.retry(exc=e, countdown=3, max_retries=None)

    sb_object = get_object(object_type, object_uuid)
    if isinstance(sb_object, Exception) is True:
        raise edit_object_task.retry(exc=sb_object, countdown=3,
                                     max_retries=None)
    elif sb_object is False:
        return sb_object
    res = sb_object.edit_content(content=content, pleb=current_pleb)

    if isinstance(res, Exception) is True:
        raise edit_object_task.retry(exc=res, countdown=3, max_retries=None)
    else:
        return res

@shared_task()
def edit_question_task(object_uuid, object_type, question_title):
    sb_object = get_object(object_type=object_type, object_uuid=object_uuid)
    if sb_object.solution_number > 0:
        return False
    if isinstance(sb_object, Exception) is True:
        raise edit_question_task.retry(exc=sb_object, countdown=3,
                                       max_retries=None)
    elif sb_object is False:
        return sb_object

    res = sb_object.edit_title(title=question_title)

    if isinstance(res, Exception) is True:
        raise edit_question_task.retry(exc=res, countdown=3, max_retries=None)
    else:
        return res