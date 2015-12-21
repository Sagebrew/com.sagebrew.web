import logging
from urllib2 import HTTPError
from django.conf import settings

from django.template.loader import render_to_string

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError, NotFoundError

from sb_questions.utils import prepare_question_search_html
logger = logging.getLogger('loggly_logs')

"""
def update_search_index_doc_script(document_id, index, field, update_value,
                                   document_type):
    '''
    This can be used if you want to update a doc in an elasticsearch index
    using a script instead of using the .update functionality provided by
    the Elasticsearch package. This may be quicker and require future testing.

    :param document_id:
    :param index:
    :param field:
    :param update_value:
    :param document_type:
    :return:
    '''
    es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
    body = {
        "script": {
            "script" : "ctx._source."+field+ " += update_value",
            "params" : {
                "update_value" : update_value
            }
        }
    }
    res = es.update(index=index, fields=["_source"], doc_type=document_type,
                    id=document_id, body=body)
    return True
"""


def process_search_result(item):
    """
    This util is called to process the search results returned from
    elasticsearch and render them to a hidden <div> element. The hidden
    div element is then accessed by javascript which uses the data in the
    element to create the div which will be displayed to users.

    :param item:
    :return:
    """
    if 'sb_score' not in item['_source']:
        item['_source']['sb_score'] = 0
    item['temp_score'] = item['_source']['sb_score'] * item['_score']
    if item['_type'] == 'question':
        item['search_html'] = prepare_question_search_html(item['_source'])
    elif item['_type'] == 'profile':
        item['search_html'] = render_to_string("user_search_block.html",
                                               item['_source'])
    elif item['_type'] == 'public_official':
        item['search_html'] = render_to_string("saga_search_block.html",
                                               item['_source'])
    return item


def update_campaign_search(campaign_data):
    try:
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        try:
            es.delete(index='full-search-base', doc_type='public_official',
                      id=campaign_data['public_official']['object_uuid'])
        except (NotFoundError, KeyError):
            pass
        es.index(index='full-search-base', doc_type='public_official',
                 id=campaign_data['id'], body=campaign_data)
        return True
    except HTTPError:
        logger.error({"function": update_campaign_search.__name__,
                      "error": "HTTPError: "})
        return False
    except TransportError:
        return False
