from celery import shared_task
from logging import getLogger

from sb_base.tasks import create_object_relations_task

from sb_notifications.tasks import spawn_notifications
from api.utils import spawn_task
from .utils import (save_post)

logger = getLogger('loggly_logs')


@shared_task()
def save_post_task(content, current_user, page_user, post_uuid, created):
    """
    Saves the post with the content sent to the task

    If the task fails the failure_dict gets sent to the queue
    :param content: "this is a post",
    :param current_pleb: "tyler.wiersing@gmail.com",
    :param wall_pleb: "devon@sagebrew.com",
    :param post_uuid: String version of a UUID
    :return:
        Returns True if the prepare_post_notification task is spawned and
        the post is successfully created
    """
    my_post = save_post(post_uuid=post_uuid, content=content, created=created)
    if isinstance(my_post, Exception) is True:
        raise save_post_task.retry(exc=my_post, countdown=3, max_retries=None)

    relation_data = {'sb_object': my_post,
                     'current_pleb': current_user,
                     'wall_pleb': page_user}
    spawned = spawn_task(task_func=create_object_relations_task,
                         task_param=relation_data)
    if isinstance(spawned, Exception):
        raise save_post_task.retry(exc=spawned, countdown=3, max_retries=None)
    notification_data = {'sb_object': my_post,
                         'from_pleb': current_user,
                         'to_plebs': [page_user,]}
    spawned = spawn_task(task_func=spawn_notifications,
                         task_param=notification_data)
    if isinstance(spawned, Exception):
        raise save_post_task.retry(exc=spawned, countdown=3, max_retries=None)
    return True