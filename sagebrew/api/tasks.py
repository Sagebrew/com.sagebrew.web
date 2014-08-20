from uuid import uuid1
from django.conf import settings
from celery import shared_task
from elasticsearch import Elasticsearch



@shared_task()
def add_object_to_search_index(index="full-search-base", object_type="", object_data=""):
    print object_data
    es = Elasticsearch([{'host': 'dwalin-us-east-1.searchly.com', 'port':443, 'use_ssl': True, 'http_auth': ('site', '6495ff8387e86cb755da1f45da88b475')}])
    res = es.index(index=index, doc_type=object_type, body=object_data)
    return True

'''
res = es.search(index='full-search', body={
  "query": {
    "filtered": {
      "query": {
        "query_string": {
          "query": "trying"
        }
      },
      "filter": {
        "term": { "user": "me" }
      }
    }
  }
})
'''
