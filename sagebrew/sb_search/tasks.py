import pytz
import traceback
import logging
from json import dumps
from uuid import uuid1
from datetime import datetime
from django.conf import settings

from celery import shared_task
from elasticsearch import Elasticsearch

from .neo_models import SearchQuery, KeyWord
from .utils import update_search_index_doc_script, update_search_index_doc
from api.utils import spawn_task
from plebs.neo_models import Pleb
from sb_posts.neo_models import SBPost
from sb_answers.neo_models import SBAnswer
from sb_questions.neo_models import SBQuestion

logger = logging.getLogger('loggly_logs')

@shared_task()
def update_weight_relationship(document_id, index, object_type="", object_uuid=str(uuid1()),
                               current_pleb="", modifier_type=""):
    '''
    This task handles creating and updating the weight relationship between
    users and: other users, questions, answers and posts. These relationships
    are used in generating more personalized search results via the
    point system

    :param object_type:
    :param object_uuid:
    :param current_pleb:
    :param modifier_type:
    :return:
    '''
    update_dict = {
        "document_id" : document_id, "index": index, "field": "sb_score",
        "document_type" : object_type, "update_value": 0
    }
    try:
        if object_type == 'question':
            question = SBQuestion.nodes.get(question_id=object_uuid)
            pleb = Pleb.nodes.get(email=current_pleb)
            if pleb.object_weight.is_connected(question):
                rel = pleb.object_weight.relationship(question)

                if rel.seen == 'seen' and modifier_type == 'search_seen':
                    rel.weight += settings.OBJECT_SEARCH_MODIFIERS[
                        'seen_search']
                    rel.save()
                    update_dict['update_value'] = rel.weight

                if modifier_type == 'comment_on':
                    rel.weight += settings.OBJECT_SEARCH_MODIFIERS[
                        'comment_on']
                    rel.status = 'commented_on'
                    rel.save()
                    update_dict['update_value'] = rel.weight

                if modifier_type == 'flag_as_inappropriate':
                    rel.weight += settings.OBJECT_SEARCH_MODIFIERS[
                        'flag_as_inappropriate']
                    rel.status = 'flagged_as_inappropriate'
                    rel.save()
                    update_dict['update_value'] = rel.weight

                if modifier_type == 'flag_as_spam':
                    rel.weight += settings.OBJECT_SEARCH_MODIFIERS[
                        'flag_as_spam']
                    rel.status = 'flagged_as_spam'
                    rel.save()
                    update_dict['update_value'] = rel.weight

                if modifier_type == 'share':
                    rel.weight += settings.OBJECT_SEARCH_MODIFIERS['share']
                    rel.status = 'shared'
                    rel.save()
                    update_dict['update_value'] = rel.weight

                if modifier_type == 'answered':
                    rel.weight += settings.OBJECT_SEARCH_MODIFIERS['answered']
                    rel.status = 'answered'
                    rel.save()
                    update_dict['update_value'] = rel.weight

                update_search_index_doc(**update_dict)

            else:
                rel = pleb.object_weight.connect(question)
                rel.save()
                update_dict['update_value'] = rel.weight
                update_search_index_doc(**update_dict)



        if object_type == 'pleb':
            pleb = Pleb.nodes.get(email=object_uuid)
            c_pleb = Pleb.nodes.get(email=current_pleb)
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

        if object_type == 'post':
            post = SBPost.nodes.get(post_id=object_uuid)
        if object_type == 'answer':
            answer = SBAnswer.nodes.get(answer_id = object_uuid)
    except Exception, e:
        logger.critical(dumps({"exception": "Unhandled Exception",
                               "function":
                                   update_weight_relationship.__name__}))
        logger.exception("Unhandled Exception: ")
        return False

@shared_task()
def add_user_to_custom_index(pleb="", index="full-search-user-specific-1"):
    '''
    This function is called when a user is created, it reindexes every document
    from the full-search-base index to the users assigned index with the
    related_user property as the new users email

    :param pleb:
    :param index:
    :return:
    '''
    res =[]
    es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
    scanres = es.search(index='full-search-base', search_type="scan",
                        scroll="10m", size=50, body={
        "query": {
            "match_all": {}
        }
    })
    scrollid = scanres['_scroll_id']

    results = es.scroll(scroll_id=scrollid, scroll='10m')
    res = results['hits']['hits']
    try:
        for item in res:
            item['_source']['related_user'] = pleb
            item['_source']['sb_score'] = 0
            if item['_type'] == 'question':
                result = es.index(index=index, doc_type='question',
                                  body=item['_source'])
            if item['_type'] == 'pleb':
                result = es.index(index=index, doc_type='pleb',
                                  body=item['_source'])
        return True
    except Exception:
        logger.critical(dumps({"exception": "Unhandled Exception",
                               "function": add_user_to_custom_index.__name__}))
        logger.exception("Unhandled Exception: ")
        return False


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
    es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
    res = es.get(index='full-search-base', doc_type=doc_type, id=doc_id)
    plebs = Pleb.category()
    for pleb in plebs.instance.all():
        #TODO update this to get index name from the users assigned index
        res['_source']['related_user'] = pleb.email
        result = es.index(index='full-search-user-specific-1', doc_type=doc_type,
                          body=res['_source'])

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
        pleb = Pleb.nodes.get(email=pleb)
        search_query = SearchQuery.nodes.get(search_query=query_param)
        rel = pleb.searches.relationship(search_query)
        rel.times_searched += 1
        rel.last_searched = datetime.now(pytz.utc)
        rel.save()
    except Pleb.DoesNotExist:
        return False
    except SearchQuery.DoesNotExist:
        search_query = SearchQuery(search_query=query_param)
        search_query.save()
        search_query.searched_by.connect(pleb)
        rel = pleb.searches.connect(search_query)
        rel.save()
        for keyword in keywords:
            keyword['query_param'] = query_param
            spawn_task(task_func=create_keyword, task_param=keyword)
    except Exception:
        logger.exception("UnhandledException: ")
        return False

@shared_task()
def create_keyword(text, relevance, query_param):
    '''

    :param keyword:
    :param relevance:
    :param query_param:
    :return:
    '''
    try:
        search_query = SearchQuery.nodes.get(search_query=query_param)
        keyword = KeyWord(keyword=text).save()
        rel = search_query.keywords.connect(keyword)
        rel.relevance = relevance
        rel.save()
        keyword.search_queries.connect(search_query)
        search_query.save()
        keyword.save()
        return True
    except SearchQuery.DoesNotExist:
        return False
    except Exception:
        logger.exception("UnhandledException: ")
        return False

