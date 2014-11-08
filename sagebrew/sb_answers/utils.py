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


def save_answer_util(content, current_pleb, question_uuid, answer_uuid=None):
    '''
    This util creates an answer and saves it, it then connects it to the
    question, and pleb

    :param content:
    :param current_pleb:
    :param answer_uuid:
    :param question_uuid:
    :return:
    '''
    if answer_uuid is None:
        answer_uuid = str(uuid1())
    try:
        try:
            my_pleb = Pleb.nodes.get(email=current_pleb)
        except (Pleb.DoesNotExist, DoesNotExist):
            return False

        try:
            question = SBQuestion.nodes.get(sb_id=question_uuid)
        except (SBQuestion.DoesNotExist, DoesNotExist) as e:
            return e

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
    except IndexError as e:
        return e
    except CypherException as e:
        return e
    except Exception as e:
        logger.exception(dumps({"function": "save_answer_util",
                                "exception": "Unhandled Exception"}))
        return e

