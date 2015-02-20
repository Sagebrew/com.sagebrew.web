import logging
from urllib2 import HTTPError
from django.conf import settings

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError

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


def update_search_index_doc(document_id, index, field, update_value,
                            document_type):
    '''
    This function can be used to update an existing document in an elasticsearch
    index. This function uses the .update functionality provided by the
    Elasticsearch python package but is also doable by using the script
    language for elasticsearch.

    :param document_id:
    :param index:
    :param field:
    :param update_value:
    :param document_type:
    :return:
    '''
    try:
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        body = {
            "doc" : {
                field : update_value
            }
        }
        res = es.update(index=index, fields=["_source"], doc_type=document_type,
                        id=document_id, body=body)
        return True
    except HTTPError:
        logger.error({"function": update_search_index_doc.__name__,
                      "error": "HTTPError: "})
        return False
    except TransportError:
        return False


def process_search_result(item):
    '''
    This util is called to process the search results returned from
    elasticsearch and render them to a hidden <div> element. The hidden
    div element is then accessed by javascript which uses the data in the
    element to create the div which will be displayed to users.

    :param item:
    :return:
    '''
    from sb_search.tasks import update_weight_relationship
    if 'sb_score' not in item['_source']:
            item['_source']['sb_score'] = 0
    if item['_type'] == 'sb_questions.neo_models.SBQuestion':
        return {"question_uuid": item['_source']['object_uuid'],
                       "type": "question",
                       "temp_score": item['_score']*item['_source']['sb_score'],
                       "score": item['_score']}
    elif item['_type'] == 'pleb':
        return {"pleb_email": item['_source']['pleb_email'],
                "type": "pleb",
                "temp_score": item['_score']*item['_source']['sb_score'],
                "score": item['_score']}
    else:
        return {'temp_score': 0}
