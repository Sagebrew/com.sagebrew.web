import pytz
from datetime import datetime

from py2neo.cypher import ClientError
from neomodel import (DoesNotExist, CypherException)

from sb_base.neo_models import SBContent


def update_masked(object_uuid):
    try:
        node = SBContent.nodes.get(object_uuid=object_uuid)
        node.is_closed = node.get_council_decision()
        node.save()
    except (SBContent.DoesNotExist, DoesNotExist, CypherException,
            ClientError, IOError) as e:
        return e

def council_decision():
    '''
    This will be called in a task which is run either everyday or every other
    day and will check which objects need to be closed
    :return:
    '''
    try:
        for node in SBContent.nodes.all():
            if (datetime.now(pytz.utc) - node.last_council_vote).days >= 5:
                node.is_closed = node.get_council_decision()
                node.save()
        return True
    except (CypherException, IOError, ClientError) as e:
        return e