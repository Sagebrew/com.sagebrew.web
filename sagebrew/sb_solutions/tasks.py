from celery import shared_task

from neomodel import CypherException

from api.utils import spawn_task
from api.tasks import add_object_to_search_index

from .neo_models import Solution


@shared_task()
def add_solution_to_search_index(solution):
    '''
    This is here to ensure idempotentence, in case cypher throws an error
    and we get back to this portion.
    '''
    try:
        solution_obj = Solution.nodes.get(object_uuid=solution["object_uuid"])
        if solution_obj.added_to_search_index is True:
            return True
    except (CypherException, IOError) as e:
        raise add_solution_to_search_index.retry(exc=e, countdown=3,
                                                 max_retries=None)
    task_data = {"object_type": "solution",
                 'object_data': solution}
    spawned = spawn_task(task_func=add_object_to_search_index,
                         task_param=task_data)
    if isinstance(spawned, Exception) is True:
        raise add_solution_to_search_index.retry(exc=spawned, countdown=3,
                                                 max_retries=None)
    try:
        solution_obj.added_to_search_index = True
        solution_obj.save()
        return True
    except (CypherException, IOError) as e:
        raise add_solution_to_search_index.retry(exc=e, countdown=3,
                                                 max_retries=None)
