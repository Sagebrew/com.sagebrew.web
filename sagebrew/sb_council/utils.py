from django.core.cache import cache

from neo4j.v1 import CypherError
from neomodel import DoesNotExist

from sagebrew.api.utils import spawn_task
from sagebrew.sb_privileges.tasks import check_privileges
from sagebrew.sb_base.neo_models import SBContent
from sagebrew.plebs.neo_models import Pleb


def update_closed(object_uuid):
    try:
        node = SBContent.nodes.get(object_uuid=object_uuid)
        node.is_closed = node.get_council_decision()
        node.save()
        cache.delete(node.object_uuid)
        return True
    except (SBContent.DoesNotExist, DoesNotExist, CypherError,
            IOError) as e:
        return e


def check_closed_reputation_changes():
    """
    This will be called in a task which is run either everyday or every other
    day and will check which objects need to be closed
    :return:
    """
    try:
        for pleb in Pleb.nodes.all():
            res = pleb.get_total_rep()
            cache.delete(pleb.username)
            if res['previous_rep'] != res['total_rep']:
                spawn_task(task_func=check_privileges,
                           task_param={'username': pleb.username})
        return True
    except (CypherError, IOError, ClientError) as e:
        return e
