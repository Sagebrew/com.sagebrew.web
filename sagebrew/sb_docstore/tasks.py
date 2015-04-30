from celery import shared_task
from boto.dynamodb2.exceptions import (JSONResponseError)

from django.conf import settings

from neomodel.exception import DoesNotExist, CypherException

from api.utils import spawn_task
from sb_public_official.neo_models import PublicOfficial
from sb_public_official.utils import get_rep_type
from sb_votes.tasks import vote_object_task

from .utils import (add_object_to_table, build_rep_page, get_user_updates)


@shared_task()
def spawn_user_updates(username, object_uuids):
    vote_res = []
    for object_uuid in object_uuids:
        try:
            vote_res.append(get_user_updates(username=username,
                                             object_uuid=object_uuid,
                                             table_name='votes'))
        except JSONResponseError as e:
            raise spawn_user_updates.retry(exc=e, countdown=10,
                                           max_retries=None)
    for item in vote_res:
        try:
            item['status'] = int(item['status'])
            task_data = {
                'vote_type': item['status'],
                'current_pleb': username,
                'object_uuid': item['parent_object'],
            }
            spawn_task(task_func=vote_object_task, task_param=task_data)
        except KeyError:
            pass


@shared_task()
def add_object_to_table_task(object_data, table):
    res = add_object_to_table(table_name=table, object_data=object_data)
    if isinstance(res, Exception) is True:
        raise add_object_to_table_task.retry(exc=res, countdown=3,
                                             max_retries=None)
    return True


@shared_task()
def build_rep_page_task(rep_id, rep_type=None):
    if rep_type is None:
        try:
            rep = PublicOfficial.nodes.get(object_uuid=rep_id)
        except (PublicOfficial.DoesNotExist, DoesNotExist,
                CypherException, IOError) as e:
            raise build_rep_page_task.retry(exc=e, countdown=3,
                                            max_retries=None)
    else:
        r_type = get_rep_type(dict(settings.BASE_REP_TYPES)[rep_type])
        try:
            rep = r_type.nodes.get(object_uuid=rep_id)
        except (r_type.DoesNotExist, DoesNotExist,
                CypherException, IOError) as e:
            return e
    res = build_rep_page(rep)
    if isinstance(res, Exception):
        raise build_rep_page_task.retry(exc=res, countdown=3, max_retries=None)
    return True
