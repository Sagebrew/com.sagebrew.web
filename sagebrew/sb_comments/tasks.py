from uuid import uuid1
from celery import shared_task

from neomodel.exception import CypherException

from sb_notifications.tasks import spawn_notifications
from api.utils import spawn_task
from sb_base.neo_models import SBContent


@shared_task()
def create_comment_relations(username, comment, parent_object):
    try:
        parent_object = SBContent.nodes.get(object_uuid=parent_object)
    except(CypherException, IOError) as e:
        raise create_comment_relations.retry(exc=e, countdown=3,
                                             max_retries=None)
    url = parent_object.get_url()
    to_plebs = []
    try:
        for pleb in parent_object.owned_by.all():
            to_plebs.append(pleb.username)
    except(CypherException, IOError) as e:
        raise create_comment_relations.retry(exc=e, countdown=3,
                                             max_retries=None)
    data = {'from_pleb': username, 'to_plebs': to_plebs, 'sb_object': comment,
            'notification_id': str(uuid1()), 'url': url}
    spawned = spawn_task(task_func=spawn_notifications, task_param=data)
    if isinstance(spawned, Exception) is True:
        raise create_comment_relations.retry(exc=spawned, countdown=3,
                                             max_retries=None)
    return True
