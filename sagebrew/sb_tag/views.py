import logging
from json import dumps
from django.conf import settings
from urllib2 import HTTPError
from requests import ConnectionError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)

from elasticsearch import Elasticsearch, helpers

from sb_base.utils import defensive_exception

logger = logging.getLogger('loggly_logs')


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_tag_view(request):
    '''
    This view returns all of the tags currently in elasticsearch. This can be
    used for pre populating tags for any time when an object can be tagged.

    :param request:
    :return:
    '''
    try:
        tag_list = []
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        scan_resp = helpers.scan(client=es, scroll='10m',
                                index='tags', doc_type='tag')
        for resp in scan_resp:
            tag_list.append(resp['_source']['tag_name'])
        return Response({'tags': tag_list}, status=200)
    except (HTTPError, ConnectionError):
        return Response({'detail': 'connection error'}, status=400)
    except Exception as e:
        return defensive_exception(get_tag_view.__name__, e, Response(
            {'tags': []}, status=400))

