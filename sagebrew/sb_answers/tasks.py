import logging
from json import dumps
from celery import shared_task

from neomodel import DoesNotExist, CypherException

from api.utils import spawn_task
from api.tasks import add_object_to_search_index
from .neo_models import SBAnswer
from plebs.neo_models import Pleb
from .utils import (save_answer_util, edit_answer_util)

logger = logging.getLogger('loggly_logs')


@shared_task()
def add_answer_to_search_index(answer):
    try:
        if answer.added_to_search_index is True:
            return True

        search_dict = {'answer_content': answer.content,
                       'user': answer.owned_by.all()[0].email,
                       'question_uuid': answer.sb_id,
                       'post_date': answer.date_created,
                       'related_user': ''}
        task_data = {"object_type": 'answer', 'object_data': search_dict,
                     "object_added": answer}
        spawned_task = spawn_task(task_func=add_object_to_search_index,
                                  task_param=task_data)
        if spawned_task is not None:
            answer.added_to_search_index = True
            answer.save()
            return True
        else:
            return False
    except IndexError as e:
        raise add_answer_to_search_index.retry(exc=e, countdown=3,
                                               max_retries=None)
    except CypherException as e:
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


@shared_task()
def edit_answer_task(content, answer_uuid, last_edited_on, current_pleb):
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
    # TODO should we notify users if things they've commented on or voted on
    # have been edited? So if the author edits their answer, notify anyone
    # related such as commenters that the question they commented on has
    # been changed or updated.
    try:
        try:
            Pleb.nodes.get(email=current_pleb)
        except (Pleb.DoesNotExist, DoesNotExist):
            return False
        try:
            SBAnswer.nodes.get(sb_id=answer_uuid)
        except (SBAnswer.DoesNotExist, DoesNotExist) as e:
            raise edit_answer_task.retry(exc=e, countdown=3, max_retries=None)

        edit_response = edit_answer_util(content=content,
                                         answer_uuid=answer_uuid,
                                         last_edited_on=last_edited_on)
        if isinstance(edit_response, Exception) is True:
            raise edit_answer_task.retry(exc=edit_response, countdown=3,
                                         max_retries=None)
        else:
            return edit_response

    except Exception as e:
        logger.exception(dumps({"function": edit_answer_task.__name__,
                                "exception": "Unhandled Exception"}))
        raise edit_answer_task.retry(exc=e, countdown=3, max_retries=None)
