import logging
from urllib2 import HTTPError
from django.conf import settings

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError, NotFoundError

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
    if item['_type'] == 'question':
        return {
            "question_uuid": item['_source']['id'],
            "type": "question",
            "temp_score": item['_score'] * item['_source']['sb_score'],
            "score": item['_score']
        }
    elif item['_type'] == 'profile':
        return {
            "username": item['_source']['id'],
            "type": "profile",
            "temp_score": item['_score'] * item['_source']['sb_score'],
            "score": item['_score']
        }
    elif item['_type'] == 'campaign' or item['_type'] == 'politicalcampaign':
        # We decided that it would be cleaner and quicker to reindex all
        # campaigns as a serialized campaign instead of a serialized public
        # official. This will future-proof ourselves for when we decide to
        # allow users to sign up for a campaign that is not for a official
        # position such as senator, house rep, president.
        return {
            "object_uuid": item['_source']['id'],
            'type': 'public_official', 'temp_score': item['_score'],
            'score': item['_score']
        }
    else:
        return {'temp_score': 0}


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
