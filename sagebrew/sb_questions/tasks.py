from uuid import uuid1
from celery import shared_task

from api.utils import spawn_task
from .utils import create_question_util

@shared_task()
def create_question_task(content="", current_pleb="", question_title=""):
    '''
    This task calls the util to create a question

    :param content:
    :param current_pleb:
    :param question_title:
    :return:
            If the create_question_util succeeds return True

            if fail retries creating the task
    '''
    if create_question_util(content, current_pleb, question_title) is not None:
        return True
    else:
        data = {'content': content, 'current_pleb': current_pleb,
                'question_title': question_title}
        spawn_task(task_func=create_question_task, task_param=data,
                   countdown=2)