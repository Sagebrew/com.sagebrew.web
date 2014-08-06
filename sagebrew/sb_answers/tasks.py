from uuid import uuid1
from celery import shared_task

from sb_notifications.tasks import create_notification_post_task
from api.utils import spawn_task
from .neo_models import SBAnswer
from plebs.neo_models import Pleb
from .utils import save_answer_util

@shared_task()
def save_answer_task(content="", current_pleb="", question_uuid="", to_pleb=""):
    #TODO Implement prepare notification for answering question
    '''
    This task is spawned when a user submits an answer to question. It then
    calls the save_answer_util to create the answer and handle creating
    the relationships.

    If the util fails the task gets called again

    :param content:
    :param current_pleb:
    :param question_uuid:
    :param to_pleb:
    :return:
    '''
    if save_answer_util(content=content, answer_uuid=str(uuid1()),
                        question_uuid=question_uuid,
                        current_pleb=current_pleb):
        return True
    else:
        data = {'content': content, 'current_pleb': current_pleb,
                'question_uuid': question_uuid}
        spawn_task(task_func=save_answer_task, task_param=data, countdown=2)
        return False

@shared_task()
def edit_answer_task(content="", answer_uuid="", last_edited_on=None,
                     current_pleb=""):
    pass

@shared_task()
def vote_answer_task(answer_uuid="", current_pleb=""):
    pass