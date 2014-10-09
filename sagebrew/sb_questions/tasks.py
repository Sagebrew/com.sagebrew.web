import logging
from uuid import uuid1
from celery import shared_task
from celery.exceptions import Retry
from django.conf import settings

from plebs.neo_models import Pleb
from .neo_models import SBQuestion
from api.utils import spawn_task
from .utils import (create_question_util, upvote_question_util,
                    downvote_question_util, edit_question_util)

logger = logging.getLogger('loggly_logs')

@shared_task()
def create_question_task(content="", current_pleb="", question_title="",
                         question_uuid=str(uuid1()), tags="", **kwargs):
    '''
    This task calls the util to create a question, if the util fails the
    task respawns itself.

    ERROR: For some reason when we expect the function to return False
        while testing it will sometimes return:
            TypeError("'DoesNotExist' object is not callable",)
        We don't know why but we must handle it

    :param content:
    :param current_pleb:
    :param question_title:
    :return:
            If the create_question_util succeeds return True

            if fail retries creating the task
    '''
    tag_list = tags.split(',')
    try:
        question = SBQuestion.nodes.get(question_id=question_uuid)
        return False
    except SBQuestion.DoesNotExist:
        response = create_question_util(content=content,
                                        current_pleb=current_pleb,
                                        question_title=question_title,
                                        tags=tag_list)
        if not response:
            raise Exception
        elif response is None:
            return False
        else:
            return True
    except TypeError:
        logger.exception({'function': create_question_task.__name__,
                          'exception': "TypeError: "})
        raise create_question_task.retry(exc=TypeError, countdown=5,
                                         max_retries=None)
    except SBQuestion.DoesNotExist:
        logger.exception({"function": create_question_task.__name__,
                          "exception": "DoesNotExist: "})
        raise edit_question_task.retry(exc=Exception, countdown=3,
                                       max_retries=None)
    except Exception:
        logger.exception({'function': create_question_task.__name__,
                          'exception': "UnhandledException: "})
        raise create_question_task.retry(exc=Exception, countdown=5,
                                         max_retries=None)

@shared_task()
def edit_question_task(question_uuid="", content="", current_pleb="",
                       last_edited_on=""):
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
        my_pleb = Pleb.nodes.get(email=current_pleb)
        my_question = SBQuestion.nodes.get(question_id=question_uuid)
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

    except SBQuestion.DoesNotExist:
        logger.exception({"function": edit_question_task.__name__,
                          "exception": "DoesNotExist: "})
        raise edit_question_task.retry(exc=Exception, countdown=3,
                                       max_retries=None)
    except Pleb.DoesNotExist:
        logger.exception({"function": edit_question_task.__name__,
                          "exception": "DoesNotExist: "})
        return False
    except Exception:
        logger.exception({"function": edit_question_task.__name__,
                          "exception": "UnhandledException: "})
        raise edit_question_task.retry(exc=Exception, countdown=3,
                                       max_retries=None)

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
    try:
        my_pleb = Pleb.nodes.get(email=current_pleb)
        my_question = SBQuestion.nodes.get(question_id=question_uuid)
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
    except SBQuestion.DoesNotExist:
        logger.exception({"function": vote_question_task.__name__,
                          "exception": "DoesNotExist: "})
        raise edit_question_task.retry(exc=Exception, countdown=3,
                                       max_retries=None)
    except Pleb.DoesNotExist:
        logger.exception({"function": vote_question_task.__name__,
                          "exception": "DoesNotExist: "})
        return False
    except Exception:
        logger.exception({"function": vote_question_task.__name__,
                          "exception": "UnhandledException: "})
        raise edit_question_task.retry(exc=Exception, countdown=3,
                                       max_retries=None)
