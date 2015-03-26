from celery import shared_task

from neomodel.exception import CypherException, DoesNotExist

from api.utils import get_object
from plebs.neo_models import Pleb


@shared_task()
def delete_object_task(object_type, object_uuid, username):
    try:
        current_pleb = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException, IOError) as e:
        raise delete_object_task.retry(exc=e, countdown=3, max_retries=None)
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
        return True