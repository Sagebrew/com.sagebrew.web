import logging

from api.utils import spawn_task
from plebs.neo_models import Pleb
from .neo_models import SBAnswer
from sb_questions.neo_models import SBQuestion

logger = logging.getLogger('loggly_logs')

def save_answer_util(content="", current_pleb="", answer_uuid="",
                     question_uuid=""):
    '''
    This util creates an answer and saves it, it then connects it to the question,
    and pleb

    :param content:
    :param current_pleb:
    :param answer_uuid:
    :param question_uuid:
    :return:
    '''
    if content=='':
        return False
    try:
        my_pleb = Pleb.nodes.get(email=current_pleb)
        question = SBQuestion.nodes.get(question_id=question_uuid)
        answer = SBAnswer(content=content, answer_id=answer_uuid)
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
        return answer
    except Pleb.DoesNotExist, SBQuestion.DoesNotExist:
        return False
    except Exception:
        logger.exception("UnhandledException: ")
        return False

def edit_answer_util(content="", current_pleb="", answer_uuid="", last_edited_on=""):
    try:
        my_answer = SBAnswer.nodes.get(answer_id=answer_uuid)
        if my_answer.to_be_deleted:
            return {'question': my_answer, 'detail': 'to be deleted'}

        if my_answer.content == content:
            return {'question': my_answer, 'detail': 'same content'}

        if my_answer.last_edited_on == last_edited_on:
            return {'question': my_answer, 'detail': 'same timestamp'}

        try:
            if my_answer.last_edited_on > last_edited_on:
                return{'question': my_answer, 'detail': 'last edit more recent'}
        except:
            pass

        my_answer.content = content
        my_answer.last_edited_on = last_edited_on
        my_answer.save()
        return True
    except SBAnswer.DoesNotExist:
        return False
    except Exception:
        logger.exception("UnhandledException: ")
        return False

def upvote_answer_util(answer_uuid="", current_pleb=""):
    from .tasks import vote_answer_task
    try:
        pleb = Pleb.nodes.get(email=current_pleb)
        my_question = SBAnswer.nodes.get(answer_id=answer_uuid)
        my_question.up_vote_number += 1
        my_question.up_voted_by.connect(pleb)
        my_question.save()
        return True
    except SBQuestion.DoesNotExist:
        data = {'question_uuid': answer_uuid, 'current_pleb': current_pleb,
                'vote_type': 'up'}
        spawn_task(task_func=vote_answer_task, task_param=data, countdown=1)
        return False
    except Pleb.DoesNotExist:
        return False
    except Exception:
        logger.exception("UnhandledException: ")
        return False


def downvote_answer_util(answer_uuid="", current_pleb=""):
    from .tasks import vote_answer_task
    try:
        pleb = Pleb.nodes.get(email=current_pleb)
        my_question = SBAnswer.nodes.get(answer_id=answer_uuid)
        my_question.down_vote_number += 1
        my_question.down_voted_by.connect(pleb)
        my_question.save()
        return True
    except SBQuestion.DoesNotExist:
        data = {'question_uuid': answer_uuid, 'current_pleb': current_pleb,
                'vote_type': 'down'}
        spawn_task(task_func=vote_answer_task, task_param=data, countdown=1)
        return False
    except Pleb.DoesNotExist:
        return False
    except Exception:
        logger.exception("UnhandledException: ")
        return False

