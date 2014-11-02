import logging
from uuid import uuid1
from json import dumps

from neomodel import CypherException, DoesNotExist

from api.utils import spawn_task
from plebs.neo_models import Pleb
from .neo_models import SBAnswer
from sb_questions.neo_models import SBQuestion
from sb_notifications.tasks import spawn_notifications

logger = logging.getLogger('loggly_logs')

def save_answer_util(content="", current_pleb="", answer_uuid="",
                     question_uuid=""):
    '''
    This util creates an answer and saves it, it then connects it to the
    question, and pleb

    :param content:
    :param current_pleb:
    :param answer_uuid:
    :param question_uuid:
    :return:
    '''
    if content=='':
        return False
    try:
        try:
            my_pleb = Pleb.nodes.get(email=current_pleb)
        except (Pleb.DoesNotExist, DoesNotExist):
            return False

        try:
            question = SBQuestion.nodes.get(sb_id=question_uuid)
        except (SBQuestion.DoesNotExist, DoesNotExist):
            return None

        answer = SBAnswer(content=content, sb_id=answer_uuid)
        answer.save()
        answer.answer_to.connect(question)
        question.answer.connect(answer)
        question.answer_number += 1
        question.save()
        rel_from_pleb = my_pleb.answers.connect(answer)
        rel_from_pleb.save()
        rel_to_pleb = answer.owned_by.connect(my_pleb)
        rel_to_pleb.save()
        answer.save()
        task_data={
            'sb_object': answer, 'from_pleb': my_pleb,
            'to_plebs': [question.owned_by.all()[0]]
        }
        spawn_task(task_func=spawn_notifications, task_param=task_data)
        return answer
    except CypherException:
        return None
    except Exception:
        logger.exception({"function": "save_answer_util", "exception":
                          "Unhandled Exception"})
        return None

def edit_answer_util(content="", current_pleb="", answer_uuid="",
                     last_edited_on=""):
    try:
        try:
            my_answer = SBAnswer.nodes.get(sb_id=answer_uuid)
        except (SBAnswer.DoesNotExist, DoesNotExist):
            return None

        if my_answer.to_be_deleted:
            return {'question': my_answer, 'detail': 'to be deleted'}

        if my_answer.content == content:
            return {'question': my_answer, 'detail': 'same content'}

        if my_answer.last_edited_on == last_edited_on:
            return {'question': my_answer, 'detail': 'same timestamp'}

        try:
            if my_answer.last_edited_on > last_edited_on:
                return{'question': my_answer,
                       'detail': 'last edit more recent'}
        except TypeError:
            pass


        edit_answer = SBAnswer(sb_id=str(uuid1()), original=False,
                               content=content).save()
        my_answer.edits.connect(edit_answer)
        edit_answer.edit_to.connect(my_answer)
        #edit_answer.owned_by.connect(my_answer.owned_by.all()[0])
        my_answer.last_edited_on = edit_answer.date_created
        my_answer.save()
        return True
    except CypherException:
        return None
    except Exception:
        logger.exception(dumps({"function": edit_answer_util.__name__,
                                "exception": "UnhandledException: "}))
        return False

def upvote_answer_util(answer_uuid="", current_pleb=""):
    from .tasks import vote_answer_task
    try:
        try:
            pleb = Pleb.nodes.get(email=current_pleb)
        except (Pleb.DoesNotExist, DoesNotExist):
            return False

        try:
            my_question = SBAnswer.nodes.get(sb_id=answer_uuid)
        except (SBAnswer.DoesNotExist, DoesNotExist):
            data = {'question_uuid': answer_uuid, 'current_pleb': current_pleb,
                    'vote_type': 'up'}
            spawn_task(task_func=vote_answer_task, task_param=data,
                       countdown=1)
            return False

        my_question.up_vote_number += 1
        my_question.up_voted_by.connect(pleb)
        my_question.save()
        return True
    except Exception:
        logger.exception(dumps({"function": upvote_answer_util.__name__,
                                "exception": "UnhandledException: "}))
        return False

def downvote_answer_util(answer_uuid="", current_pleb=""):
    from .tasks import vote_answer_task
    try:
        try:
            pleb = Pleb.nodes.get(email=current_pleb)
        except (Pleb.DoesNotExist, DoesNotExist):
            return False

        try:
            my_question = SBAnswer.nodes.get(sb_id=answer_uuid)
        except (SBAnswer.DoesNotExist, DoesNotExist):
            data = {'question_uuid': answer_uuid, 'current_pleb': current_pleb,
                'vote_type': 'down'}
            spawn_task(task_func=vote_answer_task, task_param=data, countdown=1)
            return False
        my_question.down_vote_number += 1
        my_question.down_voted_by.connect(pleb)
        my_question.save()
        return True
    except Exception:
        logger.exception(dumps({"function": downvote_answer_util.__name__,
                                "exception": "UnhandledException: "}))
        return False

def flag_answer_util(answer_uuid, current_pleb, flag_reason):
    '''
    This function will take the uuid of an answer, a pleb email, and a flag
    reason and will connect the answer to the pleb with flagged_by then
    increase the amount of flags for a particular reason supplied in
    flag_reason.

    :param answer:
    :param pleb:
    :param reason:
    :return:
    '''
    pass