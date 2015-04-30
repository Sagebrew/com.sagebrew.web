import pytz
import logging

from datetime import datetime
from django.conf import settings
from django.core.cache import cache

from celery import shared_task
from neomodel import DoesNotExist, CypherException
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import (ElasticsearchException, TransportError,
                                      ConnectionError, RequestError)

from api.utils import spawn_task
from plebs.neo_models import Pleb

from sb_base.utils import defensive_exception
from sb_base.neo_models import SBContent
from sb_questions.neo_models import Question
from sb_public_official.neo_models import PublicOfficial

from .neo_models import SearchQuery, KeyWord
from .utils import (update_search_index_doc)

logger = logging.getLogger('loggly_logs')


@shared_task()
def spawn_weight_relationships(search_items):
    for item in search_items:
        if item['_type'] == 'question':
            spawned = spawn_task(
                update_weight_relationship,
                task_param={
                    'index': item['_index'],
                    'document_id': item['_id'],
                    'object_uuid': item['_source']['object_uuid'],
                    'object_type': 'question',
                    'current_pleb': item['_source']['related_user'],
                    'modifier_type': 'seen'
                })
            if isinstance(spawned, Exception) is True:
                return spawned
        if item['_type'] == 'profile':
            spawned = spawn_task(
                update_weight_relationship,
                task_param={
                    'index': item['_index'],
                    'document_id': item['_id'],
                    'object_uuid': item['_source']['username'],
                    'object_type': 'profile',
                    'current_pleb': item['_source']['related_user'],
                    'modifier_type': 'seen'
                })
            if isinstance(spawned, Exception) is True:
                return spawned
    return True


@shared_task()
def update_weight_relationship(document_id, index, object_type,
                               object_uuid, current_pleb, modifier_type):
    '''
    This task handles creating and updating the weight relationship between
    users and: other users, questions, solutions and posts. These relationships
    are used in generating more personalized search results via the
    point system

    :param document_id:
    :param index:
    :param object_type:
    :param object_uuid:
    :param current_pleb:
    :param modifier_type:
    :return:
    '''
    update_dict = {
        "document_id": document_id, "index": index, "field": "sb_score",
        "document_type": object_type, "update_value": 0
    }
    try:
        try:
            pleb = Pleb.nodes.get(username=current_pleb)
        except (Pleb.DoesNotExist, DoesNotExist):
            return False

        if object_type == 'profile':
            try:
                pleb = Pleb.nodes.get(username=object_uuid)
                c_pleb = Pleb.nodes.get(username=current_pleb)
            except (Pleb.DoesNotExist, DoesNotExist):
                return False

            if c_pleb.user_weight.is_connected(pleb):
                rel = c_pleb.user_weight.relationship(pleb)
                if rel.interaction == 'seen' and modifier_type == 'search_seen':
                    rel.weight += settings.USER_RELATIONSHIP_MODIFIER[
                        'search_seen']
                    rel.save()
                    update_dict['update_value'] = rel.weight
                update_search_index_doc(**update_dict)
            else:
                rel = c_pleb.user_weight.connect(pleb)
                rel.save()
                update_dict['update_value'] = rel.weight
                update_search_index_doc(**update_dict)
            return True
        try:
            if object_type == "question":
                sb_object = Question.nodes.get(object_uuid=object_uuid)
            elif object_type == "saga":
                sb_object = PublicOfficial.nodes.get(object_uuid=object_uuid)
            else:
                sb_object = SBContent.nodes.get(object_uuid=object_uuid)
        except(CypherException, IOError) as e:
            raise update_weight_relationship.retry(exc=e, countdown=3,
                                                   max_retries=None)

        if pleb.object_weight.is_connected(sb_object):

            update_dict['update_value'] = \
                pleb.update_weight_relationship(sb_object, modifier_type)

            update_search_index_doc(**update_dict)
            return True
        else:
            rel = pleb.object_weight.connect(sb_object)
            rel.save()
            update_dict['update_value'] = rel.weight
            update_search_index_doc(**update_dict)
            return True
    except(CypherException, IOError) as e:
        raise update_weight_relationship.retry(exc=e, countdown=3,
                                               max_retries=None)
    except Exception as e:
        raise defensive_exception(
            update_weight_relationship.__name__, e,
            update_weight_relationship.retry(exc=e, countdown=3,
                                             max_retries=None))


@shared_task()
def add_user_to_custom_index(username=None,
                             index="full-search-user-specific-1"):
    '''
    This function is called when a user is created, it reindexes every document
    from the full-search-base index to the users assigned index with the
    related_user property as the new users email

    :param pleb:
    :param index:
    :return:
    '''
    if username is None:
        return None
    try:
        pleb = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist) as e:
        raise add_user_to_custom_index.retry(exc=e, countdown=3,
                                             max_retries=None)
    if pleb.populated_personal_index:
        return True
    es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
    if not es.indices.exists('full-search-user-specific-1'):
        es.indices.create('full-search-user-specific-1')

    scanres = es.search(
        index='full-search-base', search_type="scan", scroll="10m",
        body={
            "query": {
                "match_all": {}
            }
        })
    scrollid = scanres['_scroll_id']

    results = es.scroll(scroll_id=scrollid, scroll='10m')
    res = results['hits']['hits']
    saga_res = es.search(
        index='full-search-base', size=50, doc_type='public_official',
        body={
            "query":
                {
                    "query_string":
                        {
                            "default_field": "_type",
                            "query": "sagas"
                        }
                }
        })
    sagas = saga_res['hits']['hits']
    try:
        for item in res:
            item['_source']['related_user'] = pleb.username
            item['_source']['sb_score'] = 0
            if item['_type'] == 'question':
                es.index(index=index, doc_type='question',
                         body=item['_source'])
            if item['_type'] == 'profile':
                es.index(index=index, doc_type='profile',
                         body=item['_source'])
        for item in sagas:
            item['_source']['related_user'] = pleb.username
            item['_source']['sb_score'] = 0
            es.index(index=index, doc_type='public_official',
                     body=item['_source'])
        pleb.populated_personal_index = True
        pleb.save()
        cache.set(pleb.username, pleb)
        return True
    except Exception as e:
        raise defensive_exception(add_user_to_custom_index.__name__, e,
                                  add_user_to_custom_index.retry(
                                      exc=e, countdown=3, max_retries=None))


@shared_task()
def update_user_indices(doc_type, doc_id):
    '''
    This takes a documents type and its id in the full-search-base index,
    then gets all plebs in neo4j and adds the document from the full-search-base
    index to that users assigned index with the related_user property as
    that users email

    :param doc_type:
    :param doc_id:
    :return:
    '''
    try:
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        res = es.get(index='full-search-base', doc_type=doc_type, id=doc_id)
    except (ElasticsearchException, TransportError, ConnectionError,
            RequestError) as e:
        raise update_user_indices.retry(exc=e, countdown=3, max_retries=None)
    try:
        for pleb in Pleb.nodes.all():
            # TODO update this to get index name from the users assigned index
            res['_source']['related_user'] = pleb.username
            es.index(index='full-search-user-specific-1',
                     doc_type=doc_type, body=res['_source'])
    except (CypherException, IOError) as e:
        raise update_user_indices.retry(exc=e, countdown=3, max_retries=None)
    except (ElasticsearchException, TransportError, ConnectionError,
            RequestError) as e:
        raise update_user_indices.retry(exc=e, countdown=3, max_retries=None)

    return True


@shared_task()
def update_search_query(pleb, query_param, keywords):
    '''
    This task creates a search query node then calls the task to create and
    attach keyword nodes to the search query node

    :param pleb:
    :param query_param:
    :param keywords:
    :return:
    '''
    try:
        try:
            pleb = Pleb.nodes.get(username=pleb)
        except (Pleb.DoesNotExist, DoesNotExist, CypherException, IOError) as e:
            raise update_search_query.retry(exc=e, countdown=3,
                                            max_retries=None)
        except(CypherException, IOError) as e:
            raise update_search_query.retry(exc=e, countdown=3,
                                            max_retries=None)
        search_query = SearchQuery.nodes.get(search_query=query_param)
        if pleb.searches.is_connected(search_query):
            rel = pleb.searches.relationship(search_query)
            rel.times_searched += 1
            rel.last_searched = datetime.now(pytz.utc)
            rel.save()
            return True
        else:
            rel = pleb.searches.connect(search_query)
            rel.save()
            search_query.searched_by.connect(pleb)
            return True
    except (SearchQuery.DoesNotExist, DoesNotExist):
        search_query = SearchQuery(search_query=query_param)
        search_query.save()
        search_query.searched_by.connect(pleb)
        rel = pleb.searches.connect(search_query)
        rel.save()
        for keyword in keywords:
            keyword['query_param'] = query_param
            spawned = spawn_task(task_func=create_keyword, task_param=keyword)
            if isinstance(spawned, Exception) is True:
                return spawned
        return True
    except (CypherException, IOError) as e:
        raise update_search_query.retry(exc=e, countdown=3, max_retries=None)
    except Exception as e:
        raise update_search_query.retry(exc=e, countdown=3, max_retries=None)


@shared_task()
def create_keyword(text, relevance, query_param):
    '''
    This function takes

    :param text:
    :param relevance:
    :param query_param:
    :return:
    '''
    try:
        try:
            search_query = SearchQuery.nodes.get(search_query=query_param)
        except (SearchQuery.DoesNotExist, DoesNotExist) as e:
            raise create_keyword.retry(exc=e, countdown=3, max_retries=None)
        try:
            keyword = KeyWord.nodes.get(keyword=text)
            rel = search_query.keywords.connect(keyword)
            rel.relevance = relevance
            rel.save()
            keyword.search_queries.connect(search_query)
            search_query.save()
            keyword.save()
            return True
        except (KeyWord.DoesNotExist, DoesNotExist):
            keyword = KeyWord(keyword=text).save()
            rel = search_query.keywords.connect(keyword)
            rel.relevance = relevance
            rel.save()
            keyword.search_queries.connect(search_query)
            search_query.save()
            keyword.save()
            return True
    except (CypherException, IOError) as e:
        logger.exception("Cypher Exception: ")
        raise create_keyword.retry(exc=e, countdown=3, max_retries=None)
