import logging
from json import dumps
from celery import shared_task

from neomodel import DoesNotExist, CypherException

from api.utils import spawn_task
from api.tasks import add_object_to_search_index
from .neo_models import SBAnswer

from .utils import (save_answer_util)

logger = logging.getLogger('loggly_logs')


@shared_task()
def add_answer_to_search_index(answer):
    try:
        if answer.added_to_search_index is True:
            return True

        search_dict = {'answer_content': answer.content,
                       'user': answer.owned_by.all()[0].email,
                       'object_uuid': answer.sb_id,
                       'post_date': answer.date_created,
                       'related_user': ''}
        task_data = {"object_type": 'sb_answers.neo_models.SBAnswer',
                     'object_data': search_dict,
                     "object_added": answer}
        spawn_task(task_func=add_object_to_search_index,
                                  task_param=task_data)

        answer.added_to_search_index = True
        answer.save()
        return True
    except (IndexError, CypherException) as e:
        raise add_answer_to_search_index.retry(exc=e, countdown=3,
                                               max_retries=None)
    except Exception as e:
        logger.exception(dumps({"function": add_answer_to_search_index.__name__,
                                "exception": "Unhandled Exception"}))
        raise add_answer_to_search_index.retry(exc=e, countdown=3,
                                               max_retries=None)

@shared_task()
def save_answer_task(current_pleb, question_uuid, content):
    '''
    This task is spawned when a user submits an answer to question. It then
    calls the save_answer_util to create the answer and handle creating
    the relationships.

    If the util fails the task retries

    :param content:
    :param current_pleb:
    :param question_uuid:
    :return:
    '''
    try:
        res = save_answer_util(content=content, question_uuid=question_uuid,
                               current_pleb=current_pleb)
        if res is True:
            task_data = {'answer': res}
            return spawn_task(task_func=add_answer_to_search_index,
                              task_param=task_data)
        elif isinstance(res, Exception) is True:
            raise save_answer_task.retry(exc=res, countdown=5,
                                         max_retries=None)
        return res

    except Exception as e:
        logger.exception(dumps({"function": save_answer_task.__name__,
                                "exception": "Unhandled Exception"}))
        raise save_answer_task.retry(exc=e, countdown=5,
                                     max_retries=None)

