from django.conf import settings

from celery import shared_task
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import (ElasticsearchException, TransportError,
                                      ConnectionError, RequestError)
from neomodel import DoesNotExist, CypherException

from sb_base.utils import defensive_exception
from api.utils import spawn_task, get_object
from plebs.neo_models import Pleb
from .utils import generate_oauth_user

@shared_task()
def get_pleb_task(username, task_func, task_param):
    try:
        pleb = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist) as e:
        raise get_pleb_task.retry(exc=e, countdown=3, max_retries=None)
    except CypherException as e:
        raise get_pleb_task.retry(exc=e, countdown=3, max_retries=None)
    task_param['current_pleb'] = pleb
    success = spawn_task(task_func=task_func, task_param=task_param)

    if isinstance(success, Exception) is True:
        raise get_pleb_task.retry(exc=success, countdown=3, max_retries=None)
    else:
        return success


@shared_task()
def add_object_to_search_index(index="full-search-base", object_type="",
                               object_data=None, object_added=None):
    """
    This adds the an object to the index specified.
    :param index:
    :param object_type:
    :param object_data:
    :return:
    """
    if object_added is not None:
        if object_added.populated_es_index:
            return True
    if object_data is None:
        return False
    try:
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        try:
            res = es.index(index=index, doc_type=object_type,
                           id=object_data['object_uuid'], body=object_data)
        except KeyError:
            # TODO should this be pleb.username?
            res = es.index(index=index, doc_type=object_type,
                           id=object_data['pleb_email'], body=object_data)
    except (ElasticsearchException, TransportError, ConnectionError,
            RequestError) as e:
        raise add_object_to_search_index.retry(exc=e, countdown=3,
                                               max_retries=None)
    except Exception as e:
        raise defensive_exception(add_object_to_search_index.__name__, e,
                                  add_object_to_search_index.retry(
                                  exc=e, countdown=3, max_retries=None))


    search_id_data = {"search_data": res, "object_type": object_type,
                      "object_data": object_data,
                      "object_added": object_added}
    save_id = spawn_task(task_func=save_search_id,
                         task_param=search_id_data)
    if isinstance(save_id, Exception) is True:
        raise add_object_to_search_index.retry(exc=save_id, countdown=3,
                                               max_retries=None)

    return save_id


@shared_task
def save_search_id(search_data, object_type, object_data, object_added):
    from sb_search.tasks import update_user_indices
    task_data = {
        "doc_id": search_data['_id'],
        "doc_type": search_data['_type']
    }
    # TODO We may need to change username to sb_id internally for pleb. That
    # way the following will work and we can potentially just pass around
    # the username as the object_uuid.
    sb_object = get_object(object_type, object_data['object_uuid'])
    if isinstance(sb_object, Exception) is True:
        raise save_search_id.retry(exc=sb_object, countdown=3,
                                               max_retries=None)
    if not sb_object:
        object_added.search_id = search_data['_id']
        try:
            object_added.save()
        except CypherException as e:
            raise save_search_id.retry(exc=e, countdown=3,
                                                   max_retries=None)
    else:
        sb_object.search_id = search_data['_id']
        try:
            sb_object.save()
        except CypherException as e:
            raise save_search_id.retry(exc=e, countdown=3,
                                                   max_retries=None)

    spawned = spawn_task(task_func=update_user_indices, task_param=task_data)
    if isinstance(spawned, Exception) is True:
        raise save_search_id.retry(exc=spawned, countdown=30, max_retries=None)

    if object_added is not None:
        object_added.populated_es_index = True
        object_added.save()

@shared_task
def generate_oauth_info(username, password, web_address=None):
    res = generate_oauth_user(username, password, web_address)
    if isinstance(res, Exception):
        raise generate_oauth_info.retry(exc=res, countdown=3, max_retries=None)

    return True