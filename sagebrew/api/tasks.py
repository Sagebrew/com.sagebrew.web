from uuid import uuid1
from django.conf import settings
from api.utils import spawn_task

from celery import shared_task
from elasticsearch import Elasticsearch

from sb_questions.neo_models import SBQuestion


@shared_task()
def add_object_to_search_index(index="full-search-base", object_type="", object_data=None):
    '''
    This adds the an object to the index specified.
    :param index:
    :param object_type:
    :param object_data:
    :return:
    '''
    from sb_search.tasks import update_user_indices
    if object_data == None:
        return False
    es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
    res = es.index(index=index, doc_type=object_type, body=object_data)
    task_data = {
        "doc_id": res['_id'],
        "doc_type": res['_type']
    }

    if object_type=='question':
        question = SBQuestion.nodes.get(question_id=object_data['question_uuid'])
        question.search_id = res['_id']
        question.save()

    spawn_task(task_func=update_user_indices, task_param=task_data)
    return True