from uuid import uuid1
import logging
from celery import shared_task

from .utils import (create_notification_post_util,
                    create_notification_comment_util)

logger = logging.getLogger('loggly_logs')

@shared_task()
def create_notification_post_task(post_uuid=str(uuid1()), from_pleb="",
                                  to_pleb=""):
    '''
    This task attempts to create a notification, if it succeeds it returns True

    if it fails it spawns another one of itself and tries again
    :param data:
    :return:
    '''
    # TODO Review why create_notification_post_util has a potential to fail
    # and see if we should have a strategy other than just retring the task
    # endlessly
    try:
        if create_notification_post_util(post_uuid, from_pleb, to_pleb):
            return True
        raise Exception
    except Exception:
        raise create_notification_post_task.retry(exc=Exception, countdown=3,
                                                  max_retries=None)


@shared_task()
def create_notification_comment_task(from_pleb="", to_pleb="", comment_on="",
                                     comment_on_id="",
                                     comment_uuid=str(uuid1())):
    '''
    This task attempts to create a notification from a comment, if it
    succeeds then it return True, if not it will retry.

    :param from_pleb:
    :param to_pleb:
    :param comment_on:
    :param comment_on_id:
    :param comment_uuid:
    :return:
    '''
    # TODO Review why create_notification_post_util has a potential to fail
    # and see if we should have a strategy other than just retring the task
    # endlessly. Also need comments for this task
    try:
        res = create_notification_comment_util(from_pleb, to_pleb, comment_uuid,
                                               comment_on, comment_on_id)
        if res:
            return True
        elif res is None:
            return False
        raise Exception
    except Exception:
        raise create_notification_post_task.retry(exc=Exception, countdown=3,
                                                  max_retries=None)