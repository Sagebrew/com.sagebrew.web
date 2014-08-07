from uuid import uuid1
from celery import shared_task

from plebs.neo_models import Pleb
from .neo_models import SBQuestion
from api.utils import spawn_task
from .utils import (create_question_util, upvote_question_util,
                    downvote_question_util, edit_question_util)

@shared_task()
def create_question_task(content="", current_pleb="", question_title="",
                         question_uuid=str(uuid1())):
    '''
    This task calls the util to create a question, if the util fails the
    task respawns itself.

    :param content:
    :param current_pleb:
    :param question_title:
    :return:
            If the create_question_util succeeds return True

            if fail retries creating the task
    '''
    if create_question_util(content=content, current_pleb=current_pleb,
                            question_title=question_title) is not None:
        return True
    else:
        data = {'content': content, 'current_pleb': current_pleb,
                'question_title': question_title}
        spawn_task(task_func=create_question_task, task_param=data,
                   countdown=2)
        return False

@shared_task()
def edit_question_task(question_uuid="", content="", current_pleb="", last_edited_on=""):
    '''
    This task calls the util which determines if a question can be edited or not
    returns True and False based on how the util responds

    :param question_uuid:
    :param content:
    :param current_pleb:
    :param last_edited_on:
    :return:
    '''
    try:
        my_pleb = Pleb.index.get(email=current_pleb)
        my_question = SBQuestion.index.get(question_id=question_uuid)
        edit_question_return = edit_question_util(question_uuid=question_uuid,
                                                  content=content,
                                                  current_pleb=current_pleb,
                                                  last_edited_on=last_edited_on)
        if edit_question_return:
            return True
        if edit_question_return['detail'] == 'to be deleted':
            return False
        elif edit_question_return['detail'] == 'same content':
            return False
        elif edit_question_return['detail'] == 'same timestamp':
            return False
        elif edit_question_return['detail'] == 'last edit more recent':
            return False

    except SBQuestion.DoesNotExist, Pleb.DoesNotExist:
        return False

@shared_task()
def vote_question_task(question_uuid="", current_pleb="", vote_type=""):
    '''
    This task is spawned to create ether an upvote or downvote on a question,
    it determines if the user has already voted on this question and if they
    have does not process the vote, if they haven't the utils are called
    to create the correct type of vote

    :param question_uuid:
    :param current_pleb:
    :param vote_type:
    :return:
    '''
    my_pleb = Pleb.index.get(email=current_pleb)
    my_question = SBQuestion.index.get(question_id = question_uuid)
    if my_question.up_voted_by.is_connected(
            my_pleb) or my_question.down_voted_by.is_connected(my_pleb):
        return False
    else:
        if vote_type == 'up':
            upvote_question_util(question_uuid, current_pleb)
            return True
        elif vote_type == 'down':
            downvote_question_util(question_uuid, current_pleb)
            return True
