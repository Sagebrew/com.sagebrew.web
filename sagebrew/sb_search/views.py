from operator import itemgetter

from django.conf import settings
from django.shortcuts import render
from elasticsearch import Elasticsearch
from django.template.loader import render_to_string
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)

from api.alchemyapi import AlchemyAPI
from api.utils import (spawn_task)
from sb_registration.utils import verify_completed_registration

from .tasks import update_search_query
from .utils import process_search_result


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def search_result_view(request):
    """

    """
    return render(request, 'search.html')


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def search_result_api(request):
    """
    This is the general search rest api endpoint. It takes the query parameter
    how many results to return and the current page, as well as a filter type
    and filter parameter if they are included.

    :param request:
    :param query_param:
    :param display_num:
    :param page:
    :param filter_type:
    :param filter_param:
    :return:
    """
    # TODO Make sure calling function knows what to do with a 500 status
    # TODO can we move any of this into a util?
    query_param = request.query_params.get('q', "")
    page = int(request.query_params.get('page', 1))
    filter_type = request.query_params.get('filter', 'general')
    display_num = request.query_params.get('max_page_size', 10)
    if int(display_num) > 100:
        display_num = 100

    search_type_dict = dict(settings.SEARCH_TYPES)
    alchemyapi = AlchemyAPI()

    response = alchemyapi.keywords("text", query_param)
    # this .get on a dict is a temporary work around for the alchemyapi
    # package not having any exception handling, this will keep us safe
    # from key errors caused by us hitting the alchemy endpoint too much
    # and using up our allowed requests
    keywords = response.get('keywords', [])
    current_page = int(page)
    results = []

    # TODO surround ES query with proper exception handling and ensure
    # each one is handled correctly
    es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
    # TODO run query_param through natural language processor, determine
    # if what they have searched is an email address or a name so that
    # the first search result is that user
    # TODO implement filtering on auto generated keywords from alchemyapi
    if filter_type == 'general':
        res = es.search(
            index='full-search-base', size=50,
            body={
                "query": {
                    "query_string": {
                        "fields": ["username", "first_name", "last_name",
                                   "content", "title", "tags", "full_name"],
                        "query": query_param,
                        "phrase_slop": 2
                    }
                }
            })
    else:
        res = es.search(
            index='full-search-base', size=50,
            doc_type=search_type_dict[filter_type],
            body={
                "query": {
                    "query_string": {
                        "fields": ["username", "first_name", "last_name",
                                   "content", "title", "tags", "full_name"],
                        "query": query_param,
                        "phrase_slop": 2
                    }
                }
            })
    res = res['hits']['hits']
    task_param = {"pleb": request.user.username, "query_param": query_param,
                  "keywords": keywords}
    spawned = spawn_task(task_func=update_search_query,
                         task_param=task_param)
    if isinstance(spawned, Exception) is True:
        return Response({'detail': "server error"}, status=500)
    # TODO is this the correct way to check if res is empty? Seems to be
    # getting by this and attempting stuff further on down with no results
    if not res:
        html = render_to_string('search_result_empty.html')
        return Response({'html': html, "next": None}, status=200)
    paginator = Paginator(res, display_num)
    try:
        page = paginator.page(page)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    results = [process_search_result(item) for item in page.object_list]
    results = sorted(results, key=itemgetter('temp_score'),
                     reverse=True)

    try:
        next_page_num = page.next_page_number()
    except EmptyPage:
        next_page_num = 0
    return Response({'html': results, 'next': next_page_num},
                    status=200)
