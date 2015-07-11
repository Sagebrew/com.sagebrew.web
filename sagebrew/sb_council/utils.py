from django.core.cache import cache

from py2neo.cypher import ClientError
from neomodel import (DoesNotExist, CypherException)

from api.utils import spawn_task
from sb_privileges.tasks import check_privileges
from sb_base.neo_models import SBContent
from plebs.neo_models import Pleb

from logging import getLogger
logger = getLogger('loggly_logs')


def update_closed(object_uuid):
    try:
        node = SBContent.nodes.get(object_uuid=object_uuid)
        node.is_closed = node.get_council_decision()
        node.save()
        cache.delete(node.object_uuid)
        return True
    except (SBContent.DoesNotExist, DoesNotExist, CypherException,
            ClientError, IOError) as e:
        return e


def check_closed_reputation_changes():
    '''
    This will be called in a task which is run either everyday or every other
    day and will check which objects need to be closed
    :return:
    '''
    try:
        for pleb in Pleb.nodes.all():
            res = pleb.get_total_rep()
            cache.set(pleb.username, pleb)
            if res['previous_rep'] != res['total_rep']:
                spawn_task(task_func=check_privileges,
                           task_param={'username': pleb.username})
        return True
    except (CypherException, IOError, ClientError) as e:
        return e
