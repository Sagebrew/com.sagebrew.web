from uuid import uuid1
from celery import shared_task

from neomodel import CypherException

from api.utils import spawn_task
from api.tasks import add_object_to_search_index

from .utils import (save_answer_util)


@shared_task()
def add_answer_to_search_index(answer):
    try:
        # TODO remove added_to_search_index attribute and just query on uuid
        # to reduce the likelihood of out of sync errors occurring and not
        # needing to open up a connection with neo and es in the same task.
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
        spawned = spawn_task(task_func=add_object_to_search_index,
                             task_param=task_data)
        if isinstance(spawned, Exception) is True:
            raise add_answer_to_search_index.retry(exc=spawned, countdown=3,
                                                   max_retries=None)

        answer.added_to_search_index = True
        answer.save()
        return True
    except (IndexError, CypherException) as e:
        # TODO in the case of a CypherException there is a chance for a
        # duplicate search index object to get created. Need to resolve how
        # to stop this
        raise add_answer_to_search_index.retry(exc=e, countdown=3,
                                               max_retries=None)


@shared_task()
def save_answer_task(current_pleb, question_uuid, content, answer_uuid):
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
    # TODO we should pass a uuid to this task for the answer. That way
    # we can check if that version of the answer has already been created
    # and return from the util if so. Then we don't run the risk of
    # recreating the answer on the off chance that the search index update
    # task fails to spawn.
    res = save_answer_util(content=content, question_uuid=question_uuid,
                           current_pleb=current_pleb, answer_uuid=answer_uuid)
    if isinstance(res, Exception) is True:
        raise save_answer_task.retry(exc=res, countdown=5,
                                     max_retries=None)
    task_data = {'answer': res}
    spawned = spawn_task(task_func=add_answer_to_search_index,
                         task_param=task_data)
    if isinstance(spawned, Exception) is True:
        raise save_answer_task.retry(exc=spawned, countdown=3,
                                     max_retries=None)
    return res
