from uuid import uuid1
from celery import shared_task

from sb_posts.neo_models import SBPost
from api.utils import spawn_task
from .utils import (create_notification_post_util,
                    create_notification_comment_util)


@shared_task()
def create_notification_post_task(post_uuid=str(uuid1()), from_pleb="",
                                  to_pleb=""):
    '''
    This task attempts to create a notification, if it fails it returns True

    if it fails it spawns another one of itself and tries again
    :param data:
    :return:
    '''
    if create_notification_post_util(post_uuid, from_pleb, to_pleb):
        return True
    else:
        data={'post_uuid': post_uuid, 'from_pleb': from_pleb,
              'to_pleb': to_pleb}
        spawn_task(task_func=create_notification_post_task, task_param=data)
        return False


@shared_task()
def create_notification_comment_task(from_pleb="", to_pleb="", comment_on="",
                                     comment_on_id="", comment_uuid=str(uuid1())):
    if create_notification_comment_util(from_pleb, to_pleb, comment_uuid,
                                        comment_on, comment_on_id):
        return True
    else:
        data = {'from_pleb': from_pleb, 'to_pleb': to_pleb,
                'comment_on': comment_on, 'comment_on_id': comment_on_id,
                'comment_uuid': comment_uuid}
        spawn_task(task_func=create_notification_comment_task, task_param=data)
        return False