import logging
from uuid import uuid1
from json import dumps

from django.conf import settings

import boto.sqs
from boto.sqs.message import Message

logger = logging.getLogger('loggly_logs')


def add_failure_to_queue(message_info):
    '''
    try:
        attempt_task.apply_async([info,], countdown=countdown, task_id=task_id)
    except socket_error:
    '''
    conn = boto.sqs.connect_to_region(
        "us-west-2",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    my_queue = conn.get_queue('sb_failures')
    m = Message()
    m.set_body(message_info)
    my_queue.write(m)


def task_exception_handler(task_func):
    '''

    :param monkey_function:
    :return: monkey_wrapper function
    '''

    def task_wrapper(*args, **kwargs):
        '''
        :param args:
        :param kwargs:
        :return:
        '''
        task_info = None
        try:
            task_info = task_func(*args, **kwargs)
        except Exception:
            failure_uuid = uuid1()
            failure_dict = {
                'detail': 'failed to delete post', 'action': 'failed_task',
                'attempted_task': task_func.__name__,
                'task_info_kwargs': args[1],
                'failure_uuid': failure_uuid
            }
            logger.exception(dumps({'failure_uuid': failure_uuid}))
            add_failure_to_queue(failure_dict)
        return task_info

    return task_wrapper


