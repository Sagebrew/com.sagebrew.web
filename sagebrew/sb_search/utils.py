import traceback
import logging
from operator import itemgetter
from django.conf import settings
from django.template.loader import render_to_string

from elasticsearch import Elasticsearch

from api.utils import spawn_task
from plebs.neo_models import Pleb
from sb_questions.neo_models import SBQuestion


logger = logging.getLogger('loggly_logs')


def update_search_index_doc_script(document_id, index, field, update_value, document_type):
    es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
    body = {
        "script": {
            "script" : "ctx._source."+field+ " += update_value",
            "params" : {
                "update_value" : update_value
            }
        }
    }
    res = es.update(index=index, fields=["_source"], doc_type=document_type, id=document_id, body=body)
    return True

def update_search_index_doc(document_id, index, field, update_value,
                            document_type):
    es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
    body = {
        "doc" : {
            field : update_value
        }
    }
    res = es.update(index=index, fields=["_source"], doc_type=document_type,
                    id=document_id, body=body)
    return True

def process_search_result(item):
    '''
    This util is called to process the search results returned from
    elasticsearch and render them to a hidden <div> element
    
    :param item:
    :return:
    '''
    from sb_search.tasks import update_weight_relationship

    item['score'] = item.pop('_score')
    item['type'] = item.pop('_type')
    item['source'] = item.pop('_source')
    if item['type'] == 'question':
        spawn_task(update_weight_relationship,
                   task_param=
                   {'index': item['_index'],
                    'document_id': item['_id'],
                    'object_uuid': item['source']['question_uuid'],
                    'object_type': 'question',
                    'current_pleb': item['source']['related_user'],
                    'modifier_type': 'seen'})
        return render_to_string(
            'question_search_hidden.html', item)
    if item['type'] == 'pleb':
        spawn_task(update_weight_relationship,
                   task_param={'index': item['_index'],
                               'document_id': item['_id'],
                               'object_uuid':
                                   item['source']['pleb_email'],
                               'object_type': 'pleb',
                               'current_pleb': item['source']['related_user'],
                               'modifier_type': 'seen'})
        return render_to_string('pleb_search_hidden.html',
                                           item)