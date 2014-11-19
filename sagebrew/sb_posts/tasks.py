from json import dumps

from celery import shared_task
from logging import getLogger

from sb_notifications.tasks import spawn_notifications
from api.utils import spawn_task
from plebs.neo_models import Pleb
from .utils import (save_post)
from sb_base.utils import defensive_exception

logger = getLogger('loggly_logs')


@shared_task()
def save_post_task(content, current_pleb, wall_pleb, post_uuid=None):
    '''
    Saves the post with the content sent to the task

    If the task fails the failure_dict gets sent to the queue
    :param content: "this is a post",
    :param current_pleb: "tyler.wiersing@gmail.com",
    :param wall_pleb: "devon@sagebrew.com",
    :param post_uuid: String version of a UUID
    :return:
        Returns True if the prepare_post_notification task is spawned and
        the post is successfully created
    '''
    try:
        my_post = save_post(post_uuid=post_uuid, content=content,
                            current_pleb=current_pleb, wall_pleb=wall_pleb)
        if isinstance(my_post, Exception) is True:
            raise save_post_task.retry(exc=my_post, countdown=3,
                                       max_retries=None)
        elif my_post is False:
            return False

        else:
            current_pleb = Pleb.nodes.get(email=current_pleb)
            wall_pleb = Pleb.nodes.get(email=wall_pleb)
            notification_data={'sb_object': my_post,
                               'from_pleb': current_pleb,
                               'to_plebs': [wall_pleb,]}
            spawn_task(task_func=spawn_notifications,
                       task_param=notification_data)
            return True
    except Exception as e:
        raise defensive_exception(save_post_task.__name__, e,
                                  save_post_task.retry(exc=e, countdown=3,
                                                       max_retries=None))
