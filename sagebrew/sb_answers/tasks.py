import logging
from uuid import uuid1
from celery import shared_task

from neomodel import DoesNotExist, CypherException

from .neo_models import SBAnswer
from plebs.neo_models import Pleb
from .utils import (save_answer_util, edit_answer_util, upvote_answer_util,
                    downvote_answer_util)

logger = logging.getLogger('loggly_logs')

@shared_task()
def save_answer_task(content="", current_pleb="", question_uuid="",
                     to_pleb=""):
    '''
    This task is spawned when a user submits an answer to question. It then
    calls the save_answer_util to create the answer and handle creating
    the relationships.

    If the util fails the task retries

    :param content:
    :param current_pleb:
    :param question_uuid:
    :param to_pleb:
    :return:
    '''
    try:
        res = save_answer_util(content=content, answer_uuid=str(uuid1()),
                            question_uuid=question_uuid,
                            current_pleb=current_pleb)
        if res:
            return True
        elif res is None:
            raise TypeError
        else:
            return False
    except TypeError:
        raise save_answer_task.retry(exc=CypherException, countdown=5,
                                     max_retries=None)
    except Exception:
        logger.exception({"function": save_answer_task.__name__,
                          "exception": "UnhandledException"})
        raise save_answer_task.retry(exc=Exception, countdown=5,
                                     max_retries=None)

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
        try:
            my_pleb = Pleb.nodes.get(email=current_pleb)
        except (Pleb.DoesNotExist, DoesNotExist):
            return False

        try:
            my_answer = SBAnswer.nodes.get(answer_id=answer_uuid)
        except (SBAnswer.DoesNotExist, DoesNotExist):
            return False

        edit_response = edit_answer_util(content=content,
                                         answer_uuid=answer_uuid,
                                         current_pleb=current_pleb,
                                         last_edited_on=last_edited_on)
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
        elif edit_response is None:
            raise Exception

    except Exception:
        logger.exception({"function": edit_answer_task.__name__,
                          "exception": "UnhandledException"})
        raise edit_answer_task.retry(exc=Exception, countdown=3,
                                     max_retries=None)



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
    try:
        try:
            my_pleb = Pleb.nodes.get(email=current_pleb)
        except (Pleb.DoesNotExist, DoesNotExist):
            return False

        try:
            my_answer = SBAnswer.nodes.get(answer_id = answer_uuid)
        except (SBAnswer.DoesNotExist, DoesNotExist):
            return False

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
    except Exception:
        logger.exception({"function": edit_answer_task.__name__,
                          "exception": "vote_answer_task"})
        raise vote_answer_task.retry(exc=Exception, countdown=3,
                                     max_retries=None)