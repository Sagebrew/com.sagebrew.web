import traceback
import logging
from json import dumps
from uuid import uuid1
from traceback import print_exc
from django.conf import settings

from celery import shared_task
from elasticsearch import Elasticsearch

from .utils import update_search_index_doc_script, update_search_index_doc
from plebs.neo_models import Pleb
from sb_posts.neo_models import SBPost
from sb_answers.neo_models import SBAnswer
from sb_questions.neo_models import SBQuestion

logger = logging.getLogger('loggly_logs')

@shared_task()
def update_weight_relationship(document_id, index, object_type="", object_uuid=str(uuid1()),
                               current_pleb="", modifier_type="",
                               ):
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
        "document_type" : object_type
    }
    try:
        if object_type == 'question':
            question = SBQuestion.index.get(question_id=object_uuid)
            pleb = Pleb.index.get(email=current_pleb)
            if pleb.object_weight.is_connected(question):
                rel = pleb.object_weight.relationship(question)

                if rel.seen and modifier_type == 'seen':
                    rel.weight += settings.USER_RELATIONSHIP_MODIFIER[
                        'each_seen']
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

                print update_dict
                update_search_index_doc(**update_dict)

            else:
                rel = pleb.object_weight.connect(question)
                rel.save()
                update_dict['update_value'] = rel.weight
                update_search_index_doc(**update_dict)



        if object_type == 'pleb':
            pleb = Pleb.index.get(email=object_uuid)
            c_pleb = Pleb.index.get(email=current_pleb)
            if c_pleb.user_weight.is_connected(pleb):
                rel = c_pleb.user_weight.relationship(pleb)
                if rel.interaction and modifier_type == 'seen':
                    rel.weight += settings.USER_RELATIONSHIP_MODIFIER[
                        'each_seen']
                    rel.save()
                    update_dict['update_value'] = rel.weight
                update_search_index_doc(**update_dict)
            else:
                rel = c_pleb.user_weight.connect(pleb)
                rel.save()
                update_dict['update_value'] = rel.weight
                update_search_index_doc(**update_dict)

        if object_type == 'post':
            post = SBPost.index.get(post_id=object_uuid)
        if object_type == 'answer':
            answer = SBAnswer.index.get(answer_id = object_uuid)
    except Exception, e:
        logger.critical(dumps({"exception": "Unhandled Exception",
                               "function":
                                   update_weight_relationship.__name__}))
        logger.exception("Unhandled Exception: ")
        print_exc()
        return False

@shared_task()
def add_user_to_custom_index(pleb="", index="full-search-user-specific-1"):
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
    except Exception:
        logger.critical(dumps({"exception": "Unhandled Exception",
                               "function": add_user_to_custom_index.__name__}))
        logger.exception("Unhandled Exception: ")
        traceback.print_exc()
    return True

@shared_task()
def update_user_index(doc_type, doc_id):
    es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
    res = es.get(index='full-search-base', doc_type=doc_type, id=doc_id)
    print res
    plebs = Pleb.category()
    for pleb in plebs.instance.all():
        #TODO update this to get index name from the users assigned index
        res['_source']['related_user'] = pleb.email
        result = es.index(index='full-search-user-specific-1', doc_type=doc_type,
                          body=res['_source'])
        print result

    return True
