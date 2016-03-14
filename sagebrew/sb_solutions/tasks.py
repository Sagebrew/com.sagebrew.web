from celery import shared_task

from django.core.cache import cache

from neomodel import DoesNotExist, CypherException

from api.utils import generate_summary
from sb_solutions.neo_models import Solution


@shared_task()
def create_solution_summary_task(object_uuid):
    try:
        solution = Solution.nodes.get(object_uuid=object_uuid)
    except (DoesNotExist, Solution.DoesNotExist, CypherException, IOError) as e:
        raise create_solution_summary_task.retry(exc=e, countdown=5,
                                                 max_retries=None)
    summary = generate_summary(solution.content)
    solution.summary = summary
    solution.save()
    cache.delete(solution.object_uuid)

    return solution
