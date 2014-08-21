from uuid import uuid1
from django.conf import settings
from api.utils import spawn_task

from celery import shared_task
from elasticsearch import Elasticsearch





@shared_task()
def add_object_to_search_index(index="full-search-base", object_type="", object_data=""):
    from sb_search.tasks import update_user_index
    es = Elasticsearch([{'host': 'dwalin-us-east-1.searchly.com', 'port':443, 'use_ssl': True, 'http_auth': ('site', '6495ff8387e86cb755da1f45da88b475')}])
    res = es.index(index=index, doc_type=object_type, body=object_data)
    print res
    task_data = {
        "doc_id": res['_id'],
        "doc_type": res['_type']
    }
    spawn_task(task_func=update_user_index, task_param=task_data)
    return True


