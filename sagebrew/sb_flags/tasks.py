from celery import shared_task

from neomodel.exception import CypherException, DoesNotExist

from api.utils import get_object
from plebs.neo_models import Pleb


@shared_task()
def flag_object_task(username, object_uuid, object_type, flag_reason,
                     description=""):
    '''
    This function takes a pleb object,
    sb_object(SBSolution, SBQuestion, SBComment, SBPost), and a flag reason.
    It will then call a util to create the flag and add it to the object.

    :param current_pleb:
    :param sb_object:
    :param flag_reason:
    :return:
    '''
    try:
        current_pleb = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException, IOError) as e:
        raise flag_object_task.retry(exc=e, countdown=3, max_retries=None)
    sb_object = get_object(object_type, object_uuid)
    if isinstance(sb_object, Exception) is True:
        raise flag_object_task.retry(exc=sb_object, countdown=3,
                                     max_retries=None)
    elif sb_object is False:
        return sb_object
    res = sb_object.flag_content(flag_reason, current_pleb, description)
    if isinstance(res, Exception) is True:
        raise flag_object_task.retry(exc=res, countdown=3, max_retries=None)
    else:
        return res