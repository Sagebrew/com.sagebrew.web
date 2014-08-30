import pytz
import logging
from uuid import uuid1
from datetime import datetime
from urllib2 import HTTPError
from requests import ConnectionError
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import (api_view, permission_classes,
                                       renderer_classes)
from elasticsearch import Elasticsearch

from api.utils import (get_post_data, spawn_task, post_to_api)

logger = logging.getLogger('loggly_logs')

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def create_tag_view(request):
    pass

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_tag_view(request, query_param):
    es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
    search_query = {
        "query": {
            "query_string": {
                "query": query_param
            }
        },
        "filter": {
            "type": {
                "value": "tags"
            }
        }
    }
    res = es.search(index='full-search-base', size=50,
                    body=search_query)
