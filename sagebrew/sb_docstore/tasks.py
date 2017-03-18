from celery import shared_task
from boto.dynamodb2.exceptions import (JSONResponseError)
from boto.exception import BotoClientError, BotoServerError, AWSConnectionError

from sagebrew.api.utils import spawn_task

from sagebrew.sb_docstore.utils import (add_object_to_table, get_user_updates)


@shared_task()
def spawn_user_updates(username, object_uuid):
    from sagebrew.sb_votes.tasks import vote_object_task
    vote_res = []
    try:
        vote_res.append(get_user_updates(username=username,
                                         object_uuid=object_uuid,
                                         table_name='votes'))
    except JSONResponseError as e:
        raise spawn_user_updates.retry(exc=e, countdown=10,
                                       max_retries=None)
    except(TypeError, IOError, BotoClientError,
           BotoServerError, AWSConnectionError, Exception) as e:
        raise spawn_user_updates.retry(exc=e, countdown=45,
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

    return True


@shared_task()
def add_object_to_table_task(object_data, table):
    try:
        add_object_to_table(table_name=table, object_data=object_data)
    except(TypeError, IOError, BotoClientError,
           BotoServerError, AWSConnectionError, Exception) as e:
        raise add_object_to_table_task.retry(exc=e, countdown=3,
                                             max_retries=None)
    return True
