import logging
from json import dumps
from urllib2 import HTTPError
from django.conf import settings

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError

from api.utils import spawn_task

logger = logging.getLogger('loggly_logs')


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
    try:
        print item
        if 'sb_score' not in item['_source']:
                item['_source']['sb_score'] = 0
        if item['_type'] == 'sb_questions.neo_models.SBQuestion':
            spawn_task(update_weight_relationship,
                       task_param=
                       {'index': item['_index'],
                        'document_id': item['_id'],
                        'object_uuid': item['_source']['object_uuid'],
                        'object_type': 'question',
                        'current_pleb': item['_source']['related_user'],
                        'modifier_type': 'seen'})
            return {"question_uuid": item['_source']['object_uuid'],
                           "type": "question",
                           "temp_score": item['_score']*item['_source']['sb_score'],
                           "score": item['_score']}
        if item['_type'] == 'pleb':
            spawn_task(update_weight_relationship,
                       task_param={'index': item['_index'],
                                   'document_id': item['_id'],
                                   'object_uuid':
                                       item['_source']['pleb_email'],
                                   'object_type': 'pleb',
                                   'current_pleb': item['_source']['related_user'],
                                   'modifier_type': 'seen'})
            return {"pleb_email": item['_source']['pleb_email'],
                           "type": "pleb",
                           "temp_score": item['_score']*item['_source']['sb_score'],
                           "score": item['_score']}
    except Exception:
        logger.exception(dumps({"function": process_search_result.__name__,
                                "exception": "Unhandled Exception"}))
        return {}

# TODO can we pass the actual object or the string of the object, get it
# and store the modifier in the object itself as a variable rather than
# in a dict in settings? That way when we add additional objects that
# create modifiers to the weight we just store the value in say
# search_weight_modifier on the object and when passed here it knows what to do
# with it
# Flagging seems to be the only one with multiple options but maybe we could
# turn it into a function that takes some attributes associated with the model
# such as get_search_modifier_weight(*args) where we can pass it a reason or
# nothing and it determines what to do with it.
# Primary goal is to not have to modify this function every time we have a new
# search object.
def update_weight_relationship_values(rel, modifier_type):
    if rel.seen is True and modifier_type == 'search_seen':
        rel.weight += settings.OBJECT_SEARCH_MODIFIERS[
            'seen_search']
        rel.save()
        return rel.weight

    if modifier_type == 'comment_on':
        rel.weight += settings.OBJECT_SEARCH_MODIFIERS[
            'comment_on']
        rel.status = 'commented_on'
        rel.save()
        return rel.weight

    if modifier_type == 'flag_as_inappropriate':
        rel.weight += settings.OBJECT_SEARCH_MODIFIERS[
            'flag_as_inappropriate']
        rel.status = 'flagged_as_inappropriate'
        rel.save()
        return rel.weight

    if modifier_type == 'flag_as_spam':
        rel.weight += settings.OBJECT_SEARCH_MODIFIERS[
            'flag_as_spam']
        rel.status = 'flagged_as_spam'
        rel.save()
        return rel.weight

    if modifier_type == 'share':
        rel.weight += settings.OBJECT_SEARCH_MODIFIERS['share']
        rel.status = 'shared'
        rel.save()
        return rel.weight

    if modifier_type == 'answered':
        rel.weight += settings.OBJECT_SEARCH_MODIFIERS['answered']
        rel.status = 'answered'
        rel.save()
        return rel.weight