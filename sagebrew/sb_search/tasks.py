import pytz
import logging
from datetime import datetime

from py2neo.cypher.error import ClientError
from celery import shared_task
from neomodel import DoesNotExist, CypherException

from api.utils import spawn_task
from plebs.neo_models import Pleb

from .neo_models import SearchQuery, KeyWord

logger = logging.getLogger('loggly_logs')


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
            pleb = Pleb.get(username=pleb)
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
    except (CypherException, IOError, ClientError) as e:
        logger.exception("Cypher Exception: ")
        raise create_keyword.retry(exc=e, countdown=3, max_retries=None)
