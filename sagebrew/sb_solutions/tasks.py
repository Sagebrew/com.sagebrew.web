from celery import shared_task

from django.core.cache import cache

from neo4j.v1 import CypherError
from neomodel import DoesNotExist

from sagebrew.api.utils import generate_summary
from sagebrew.sb_solutions.neo_models import Solution


@shared_task()
def create_solution_summary_task(object_uuid):
    try:
        solution = Solution.nodes.get(object_uuid=object_uuid)
    except (DoesNotExist, Solution.DoesNotExist, CypherError, IOError) as e:
        raise create_solution_summary_task.retry(exc=e, countdown=5,
                                                 max_retries=None)
    summary = generate_summary(solution.content)
    if summary is not None and summary != "":
        solution.summary = summary
    solution.save()
    cache.delete(solution.object_uuid)

    return solution
