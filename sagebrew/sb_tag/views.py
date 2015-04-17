from django.conf import settings
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)

from elasticsearch import Elasticsearch, helpers


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_tag_view(request):
    '''
    This view returns all of the tags currently in elasticsearch. This can be
    used for pre populating tags for any time when an object can be tagged.

    :param request:
    :return:
    '''
    tag_list = []
    es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
    scan_resp = helpers.scan(client=es, scroll='10m',
                             index='tags', doc_type='tag')

    for resp in scan_resp:
        tag_list.append({"value": resp['_source']['name']})
    return Response({'tags': tag_list}, status=200)

