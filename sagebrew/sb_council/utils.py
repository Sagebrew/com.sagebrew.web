import pytz
from datetime import datetime

from django.core.cache import cache

from py2neo.cypher import ClientError
from neomodel import (DoesNotExist, CypherException)

from sb_base.neo_models import SBContent
from plebs.neo_models import Pleb

from logging import getLogger
logger = getLogger('loggly_logs')


def update_closed(object_uuid):
    try:
        node = SBContent.nodes.get(object_uuid=object_uuid)
        node.is_closed = node.get_council_decision()
        node.save()
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
        for node in SBContent.nodes.all():
            if (datetime.now(pytz.utc) - node.initial_council_vote).days >= 5:
                owner = Pleb.nodes.get(object_uuid=node.owner_username)
                owner.get_total_rep()
                owner.refresh()
                cache.set(owner.username, owner)
        return True
    except (CypherException, IOError, ClientError) as e:
        return e