import logging
from celery import shared_task

from neomodel.exception import CypherException, DoesNotExist

from plebs.neo_models import Pleb
from .utils import create_notification_util

logger = logging.getLogger('loggly_logs')


@shared_task()
def spawn_notifications(sb_object, from_pleb, to_plebs, uuid=None):
    '''
    This function will take an object(post,comment,solution,etc.), the type of
    the object, from_pleb and a to_pleb. To pleb can be a list of people or
    just a singular pleb and will create a notification about the object

    :param sb_object:
    :param from_pleb:
    :param to_plebs:
    :param uuid
    :return:
    '''
    plebeians = []
    try:
        from_pleb = Pleb.nodes.get(username=from_pleb)
    except(CypherException, Pleb.DoesNotExist, DoesNotExist) as e:
        raise spawn_notifications.retry(exc=e, countdown=3, max_retries=None)

    for plebeian in to_plebs:
        try:
            to_pleb = Pleb.nodes.get(username=plebeian)
            plebeians.append(to_pleb)
        except(CypherException, Pleb.DoesNotExist, DoesNotExist) as e:
            raise spawn_notifications.retry(exc=e, countdown=3,
                                            max_retries=None)
    response = create_notification_util(sb_object, from_pleb, plebeians, uuid)

    if isinstance(response, Exception) is True:
        raise spawn_notifications.retry(exc=response, countdown=3,
                                        max_retries=None)
    return response

