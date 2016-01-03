import logging
from urllib2 import HTTPError
from django.conf import settings

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError, NotFoundError

logger = logging.getLogger('loggly_logs')


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


def remove_search_object(object_uuid, object_type, index="full-search-base"):
    try:
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        try:
            es.delete(index=index, doc_type=object_type, id=object_uuid)
        except NotFoundError:
            pass
        return True
    except TransportError:
        return False
