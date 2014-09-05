import pytz
import logging
import traceback
from django.conf import settings
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)

from elasticsearch import Elasticsearch, helpers

from api.utils import (get_post_data, spawn_task, post_to_api)

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
        #TODO once we have an index specifically for tags, update this index
        scanResp = helpers.scan(client=es, scroll='10m',
                                index='full-search-base', doc_type='tag')
        for resp in scanResp:
            tag_list.append(resp['_source']['tag_name'])
        return Response({'tags': tag_list}, status=200)
    except Exception:
        traceback.print_exc()
        return Response({'tags': []}, status=400)

