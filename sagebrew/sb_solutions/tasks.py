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
from sb_base.tasks import create_object_relations_task
from sb_questions.neo_models import SBQuestion
from .utils import (save_solution_util)


@shared_task()
def add_solution_to_search_index(solution):
    try:
        try:
            es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
            res = es.get(index='full-search-base',
                         doc_type='sb_solutions.neo_models.SBSolution',
                         id=solution.object_uuid)
            return True
        except NotFoundError:
            pass
        except (ElasticsearchException, TransportError, ConnectionError,
                RequestError) as e:
            raise add_solution_to_search_index.retry(exc=e, countdown=3,
                                                   max_retries=None)
        try:
            solution_owner = solution.owned_by.all()[0].email
        except IndexError as e:
            raise add_solution_to_search_index.retry(exc=e, countdown=3,
                                                   max_retries=None)
        search_dict = {'solution_content': solution.content,
                       'user': solution_owner,
                       'object_uuid': solution.object_uuid,
                       'post_date': solution.created,
                       'related_user': ''}
        task_data = {"object_type": 'sb_solutions.neo_models.SBSolution',
                     'object_data': search_dict}
        spawned = spawn_task(task_func=add_object_to_search_index,
                             task_param=task_data)
        if isinstance(spawned, Exception) is True:
            raise add_solution_to_search_index.retry(exc=spawned, countdown=3,
                                                   max_retries=None)

        solution.added_to_search_index = True
        solution.save()
        return True
    except (CypherException) as e:
        raise add_solution_to_search_index.retry(exc=e, countdown=3,
                                               max_retries=None)


@shared_task()
def save_solution_task(current_pleb, question_uuid, content, solution_uuid):
    '''
    This task is spawned when a user submits an solution to question. It then
    calls the save_solution_util to create the solution and handle creating
    the relationships.

    If the util fails the task retries

    :param content:
    :param current_pleb:
    :param question_uuid:
    :return:
    '''
    solution = save_solution_util(content=content, solution_uuid=solution_uuid)
    if isinstance(solution, Exception) is True:
        raise save_solution_task.retry(exc=solution, countdown=5, max_retries=None)

    relation_data = {"sb_object": solution, "current_pleb": current_pleb,
                     "question": question_uuid}
    spawned = spawn_task(task_func=create_object_relations_task,
                         task_param=relation_data)
    if isinstance(spawned, Exception):
        raise save_solution_task.retry(exc=spawned, countdown=3, max_retries=None)

    task_data = {'solution': solution}
    spawned = spawn_task(task_func=add_solution_to_search_index,
                         task_param=task_data)
    if isinstance(spawned, Exception) is True:
        raise save_solution_task.retry(exc=spawned, countdown=3, max_retries=None)

    try:
        question = SBQuestion.nodes.get(object_uuid=question_uuid)
    except(CypherException, SBQuestion.DoesNotExist, DoesNotExist) as e:
        raise save_solution_task.retry(exc=e, countdown=3, max_retries=None)
    try:
        to_pleb = [question.owned_by.all()[0].email]
    except IndexError as e:
        raise save_solution_task.retry(exc=e, countdown=3, max_retries=None)

    task_data={'sb_object': solution, 'from_pleb': current_pleb,
               'to_plebs': to_pleb}
    spawn_task(task_func=spawn_notifications, task_param=task_data)
    if isinstance(spawned, Exception) is True:
        raise save_solution_task.retry(exc=spawned, countdown=3, max_retries=None)

    return solution
