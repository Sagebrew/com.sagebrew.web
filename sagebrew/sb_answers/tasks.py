from celery import shared_task
from django.conf import settings

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import (ElasticsearchException, TransportError,
                                      ConnectionError, RequestError,
                                      NotFoundError)
from neomodel import CypherException, DoesNotExist


from api.utils import spawn_task
from api.tasks import add_object_to_search_index
from sb_notifications.tasks import spawn_notifications
from sb_docstore.tasks import add_object_to_table_task
from sb_base.tasks import create_object_relations_task
from sb_questions.neo_models import SBQuestion
from .utils import (save_answer_util)


@shared_task()
def add_answer_to_search_index(answer):
    try:
        try:
            es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
            res = es.get(index='full-search-base',
                         doc_type='sb_answers.neo_models.SBAnswer',
                         id=answer.sb_id)
            return True
        except NotFoundError:
            pass
        except (ElasticsearchException, TransportError, ConnectionError,
                RequestError) as e:
            raise add_answer_to_search_index.retry(exc=e, countdown=3,
                                                   max_retries=None)
        try:
            answer_owner = answer.owned_by.all()[0].email
        except IndexError as e:
            raise add_answer_to_search_index.retry(exc=e, countdown=3,
                                                   max_retries=None)
        search_dict = {'answer_content': answer.content,
                       'user': answer_owner,
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
    except (CypherException) as e:
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
    answer = save_answer_util(content=content, answer_uuid=answer_uuid)
    if isinstance(answer, Exception) is True:
        raise save_answer_task.retry(exc=answer, countdown=5, max_retries=None)

    relation_data = {"sb_object": answer, "current_pleb": current_pleb,
                     "question": question_uuid}
    spawned = spawn_task(task_func=create_object_relations_task,
                         task_param=relation_data)
    if isinstance(spawned, Exception):
        raise save_answer_task.retry(exc=spawned, countdown=3, max_retries=None)

    task_data = {'answer': answer}
    spawned = spawn_task(task_func=add_answer_to_search_index,
                         task_param=task_data)
    if isinstance(spawned, Exception) is True:
        raise save_answer_task.retry(exc=spawned, countdown=3, max_retries=None)

    try:
        question = SBQuestion.nodes.get(sb_id=question_uuid)
    except(CypherException, SBQuestion.DoesNotExist, DoesNotExist):
        raise save_answer_task.retry(exc=spawned, countdown=3, max_retries=None)
    try:
        to_pleb = question.owned_by.all()[0].email
    except IndexError as e:
        raise save_answer_task.retry(exc=e, countdown=3, max_retries=None)

    task_data={'sb_object': answer, 'from_pleb': current_pleb,
               'to_plebs': to_pleb}
    spawn_task(task_func=spawn_notifications, task_param=task_data)
    if isinstance(spawned, Exception) is True:
        raise save_answer_task.retry(exc=spawned, countdown=3, max_retries=None)

    return answer
