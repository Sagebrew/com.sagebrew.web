import logging
from django.conf import settings

from celery import shared_task
from elasticsearch import Elasticsearch

from sb_base.utils import defensive_exception

from api.utils import spawn_task, get_object

logger = logging.getLogger('loggly_logs')


@shared_task()
def add_object_to_search_index(index="full-search-base", object_type="",
                               object_data=None, object_added=None):
    '''
    This adds the an object to the index specified.
    :param index:
    :param object_type:
    :param object_data:
    :return:
    '''
    from sb_search.tasks import update_user_indices
    if object_added is not None:
        if object_added.populated_es_index:
            return True
    try:
        if object_data is None:
            return False
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        res = es.index(index=index, doc_type=object_type, body=object_data)
        task_data = {
            "doc_id": res['_id'],
            "doc_type": res['_type']
        }
        if object_added is not None:
            return True

        sb_object = get_object(object_type, object_data['object_uuid'])
        if isinstance(sb_object, Exception) is True:
            raise sb_object
        sb_object.search_id = res['_id']
        sb_object.save()

        spawn_task(task_func=update_user_indices, task_param=task_data)
        if object_added is not None:
            object_added.populated_es_index = True
            object_added.save()
        return True
    except Exception as e:
        raise defensive_exception(add_object_to_search_index.__name__, e,
                            add_object_to_search_index.retry(exc=e, countdown=3,
                                               max_retries=None))