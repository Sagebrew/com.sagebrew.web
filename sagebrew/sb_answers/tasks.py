from uuid import uuid1
from celery import shared_task

from sb_notifications.tasks import create_notification_post_task
from api.utils import spawn_task
from .neo_models import SBAnswer
from plebs.neo_models import Pleb
from .utils import (save_answer_util, edit_answer_util, upvote_answer_util,
                    downvote_answer_util)

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
    '''
    This task is spawned when a user attempts to edit an answer. It calls
    the edit_answer util to edit the answer and the return is based upon
    what the util returns

    :param content:
    :param answer_uuid:
    :param last_edited_on:
    :param current_pleb:
    :return:
    '''
    try:
        my_pleb = Pleb.index.get(email=current_pleb)
        my_answer = SBAnswer.index.get(answer_id=answer_uuid)
        edit_response = edit_answer_util(content=content, answer_uuid=answer_uuid,
                            current_pleb=current_pleb, last_edited_on=last_edited_on)
        if edit_response:
            return True
        if edit_response['detail'] == 'to be deleted':
            return False
        elif edit_response['detail'] == 'same content':
            return False
        elif edit_response['detail'] == 'same timestamp':
            return False
        elif edit_response['detail'] == 'last edit more recent':
            return False

    except SBAnswer.DoesNotExist, Pleb.DoesNotExist:
        return False



@shared_task()
def vote_answer_task(answer_uuid="", current_pleb="", vote_type=""):
    '''
    This task is spawned when a user attempts to upvote or downvote an answer,
    It determines if they have already voted on this answer and if they haven't
    it calls a util and creates the vote based on which vote_type is passed

    :param answer_uuid:
    :param current_pleb:
    :param vote_type:
    :return:
    '''
    my_pleb = Pleb.index.get(email=current_pleb)
    my_answer = SBAnswer.index.get(answer_id = answer_uuid)
    if my_answer.up_voted_by.is_connected(
            my_pleb) or my_answer.down_voted_by.is_connected(my_pleb):
        return False
    else:
        if vote_type == 'up':
            upvote_answer_util(answer_uuid, current_pleb)
            return True
        elif vote_type == 'down':
            downvote_answer_util(answer_uuid, current_pleb)
            return True