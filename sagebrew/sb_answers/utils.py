from uuid import uuid1

from neomodel import CypherException, DoesNotExist

from api.utils import spawn_task
from plebs.neo_models import Pleb
from sb_base.utils import defensive_exception
from sb_questions.neo_models import SBQuestion
from sb_notifications.tasks import spawn_notifications
from sb_base.tasks import create_object_relations_task

from .neo_models import SBAnswer


def save_answer_util(content, current_pleb, question_uuid, answer_uuid):
    '''
    This util creates an answer and saves it, it then connects it to the
    question, and pleb

    :param content:
    :param current_pleb:
    :param answer_uuid:
    :param question_uuid:
    :return:
    '''
    try:
        try:
            my_pleb = Pleb.nodes.get(email=current_pleb)
        except (Pleb.DoesNotExist, DoesNotExist) as e:
            return e

        try:
            question = SBQuestion.nodes.get(sb_id=question_uuid)
        except (SBQuestion.DoesNotExist, DoesNotExist) as e:
            return e

        answer = SBAnswer(content=content, sb_id=answer_uuid)
        answer.save()
        relation_data = {"sb_object": answer, "current_pleb": my_pleb,
                         "question": question}
        spawn_task(task_func=create_object_relations_task,
                   task_param=relation_data)
        task_data={
            'sb_object': answer, 'from_pleb': my_pleb,
            'to_plebs': [question.owned_by.all()[0]]
        }
        spawn_task(task_func=spawn_notifications, task_param=task_data)
        return answer
    except (IndexError, CypherException) as e:
        return e
    except Exception as e:
        return defensive_exception(save_answer_util.__name__, e, e)

