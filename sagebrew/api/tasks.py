import logging

from django.conf import settings

from celery import shared_task
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import (ElasticsearchException, TransportError,
                                      ConnectionError, RequestError)
from neomodel import CypherException, db

from sb_search.neo_models import Searchable

from .utils import spawn_task


logger = logging.getLogger('loggly_logs')


@shared_task()
def add_object_to_search_index(object_uuid, object_data,
                               index="full-search-base"):
    """
    This adds the an object to the index specified.
    :param index:
    :param object_type:
    :param object_data:
    :return:
    """
    try:
        query = 'MATCH (a:Searchable) WHERE a.object_uuid = ' \
                '"%s" RETURN a' % (object_uuid)
        res, col = db.cypher_query(query)
        try:
            object_added = Searchable.inflate(res[0][0])
        except IndexError:
            logger.exception("Failed to find any searchable content")
            return False
    except(CypherException, IOError) as e:
        logger.exception("Failed to Connect to Neo in Search Index")
        raise add_object_to_search_index.retry(exc=e, countdown=3,
                                               max_retries=None)
    if object_added is not None:
        if object_added.populated_es_index is True:
            return True
    else:
        return False
    try:
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        res = es.index(index=index, doc_type=object_data['type'],
                       id=object_data['id'], body=object_data)
    except (ElasticsearchException, TransportError, ConnectionError,
            RequestError) as e:
        logger.exception("Failed to Connect to Elastic Search")
        raise add_object_to_search_index.retry(exc=e, countdown=3,
                                               max_retries=None)
    except KeyError:
        # If the correct values are provided then there's no reason to keep
        # retrying
        return False
    except Exception as e:
        logger.exception("Unhandled Exception in Storing to Index")
        raise add_object_to_search_index.retry(exc=e, countdown=3,
                                               max_retries=10)

    search_id_data = {
        "search_data": res,
        "object_uuid": object_uuid,
    }
    save_id = spawn_task(task_func=save_search_id, task_param=search_id_data)
    if isinstance(save_id, Exception) is True:
        raise add_object_to_search_index.retry(exc=save_id, countdown=3,
                                               max_retries=None)

    return save_id


@shared_task
def save_search_id(search_data, object_uuid):
    from sb_search.tasks import update_user_indices
    task_data = {
        "doc_id": search_data['_id'],
        "doc_type": search_data['_type']
    }
    try:
        query = 'MATCH (a:Searchable) WHERE a.object_uuid = ' \
                '"%s" RETURN a' % (object_uuid)
        res, col = db.cypher_query(query)
        try:
            sb_object = Searchable.inflate(res[0][0])
        except IndexError:
            logger.exception("Failed to find any searchable content")
            return False

    except(CypherException, IOError) as e:
        raise save_search_id.retry(exc=e, countdown=3, max_retries=None)

    sb_object.search_id = search_data['_id']
    sb_object.populated_es_index = True
    try:
        sb_object.save()
    except(CypherException, IOError) as e:
        raise save_search_id.retry(exc=e, countdown=3, max_retries=None)

    spawned = spawn_task(task_func=update_user_indices, task_param=task_data)
    if isinstance(spawned, Exception) is True:
        raise save_search_id.retry(exc=spawned, countdown=30, max_retries=None)
