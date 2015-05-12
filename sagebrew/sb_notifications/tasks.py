import logging
from celery import shared_task

from neomodel.exception import CypherException, DoesNotExist

from plebs.neo_models import Pleb
from .utils import create_notification_util

logger = logging.getLogger('loggly_logs')


@shared_task()
def spawn_notifications(sb_object, from_pleb, to_plebs, notification_id, url,
                        action_name):
    '''
    This function will take an object(post,comment,solution,etc.), the type of
    the object, from_pleb and a to_pleb. To pleb can be a list of people or
    just a singular pleb and will create a notification about the object

    :param sb_object:
    :param from_pleb:
    :param to_plebs:
    :param notification_id
    :return:
    '''
    plebeians = []
    if from_pleb in to_plebs:
        to_plebs.remove(from_pleb)
    try:
        from_pleb = Pleb.get(username=from_pleb)
    except(CypherException, Pleb.DoesNotExist, DoesNotExist, IOError) as e:
        raise spawn_notifications.retry(exc=e, countdown=3, max_retries=100)

    for plebeian in to_plebs:
        try:
            to_pleb = Pleb.get(username=plebeian)
            plebeians.append(to_pleb)
        except(CypherException, Pleb.DoesNotExist, DoesNotExist, IOError) as e:
            raise spawn_notifications.retry(exc=e, countdown=3, max_retries=100)
    response = create_notification_util(sb_object, from_pleb, plebeians,
                                        notification_id, url, action_name)

    if isinstance(response, Exception) is True:
        raise spawn_notifications.retry(exc=response, countdown=3,
                                        max_retries=100)
    return response
