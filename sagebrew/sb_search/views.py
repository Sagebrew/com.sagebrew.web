import logging
from json import dumps
from operator import itemgetter
from django.conf import settings
from multiprocessing import Pool
from django.shortcuts import render, redirect
from elasticsearch import Elasticsearch
from django.template.loader import render_to_string
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)

from neomodel import DoesNotExist

from .tasks import update_search_query
from .utils import process_search_result
from .forms import SearchForm, SearchFormApi
from api.alchemyapi import AlchemyAPI
from api.utils import (spawn_task)
from plebs.neo_models import Pleb
from plebs.utils import prepare_user_search_html
from sb_search.tasks import update_weight_relationship
from sb_questions.utils import prepare_question_search_html
from sb_registration.utils import verify_completed_registration

logger = logging.getLogger('loggly_logs')


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def search_view(request):
    '''
    This view serves the main search page. This page may be removed later
    because having the search results and search bar on the same page may be
    beneficial and easier to lay out.

    :param request:
    :return:
    '''
    try:
        pleb = Pleb.nodes.get(email=request.user.email)
    except (Pleb.DoesNotExist, DoesNotExist):
        return redirect('404_error')
    return render(request, 'search_page.html', {"pleb_info": pleb})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def search_result_view(request, query_param, display_num=5, page=1,
                       range_start=0, range_end=10):
    '''
    This view serves the page that holds the search results.

    :param request:
    :param query_param:
    :param display_num:
    :param page:
    :param range_start:
    :param range_end:
    :return:
    '''
    pleb = Pleb.nodes.get(email=request.user.email)
    search_data = {'query_param': query_param, 'page': page, 'display_num':
                   display_num, 'range_start': range_start,
                   'range_end': range_end}
    search_form = SearchForm(search_data)
    if search_form.is_valid():
        return render(request, 'search_result.html',
                      {'search_param': search_form.cleaned_data['query_param'],
                       'page': search_form.cleaned_data['page'],
                       'pleb_info': pleb}, status=200)
    else:
        return render(request, 'search_result.html', {'pleb_info': pleb},status=400)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def search_result_api(request, query_param="", display_num=10, page=1,
                      filter_type="", filter_param=""):
    '''
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
    '''
    data = {'query_param': query_param, 'display_num': display_num,
            'page': int(page),
            'filter_type': filter_type, 'filter_param': filter_param}
    search_form = SearchFormApi(data)
    if search_form.is_valid():
        alchemyapi = AlchemyAPI()
        response = alchemyapi.keywords("text", search_form.cleaned_data[
                                      'query_param'])
        current_page = int(search_form.cleaned_data['page'])
        results=[]
        current_user_email = request.user.email
        current_user_email,current_user_address = current_user_email.split('@')

        try:
            es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
            #TODO benchmark getting the index from neo vs. getting from postgres
            #TODO run query_param through natural language processor, determine
            #if what they have searched is an email address or a name so that
            #the first search result is that user
            #TODO implement filtering on auto generated keywords from alchemyapi
            #TODO change using the current_user_email to the users
            #username
            res = es.search(index='full-search-user-specific-1', size=50,
                            body=
                            {
                                "query": {
                                    "query_string": {
                                        "query": search_form.cleaned_data[
                                            'query_param']
                                    }
                                },
                                "filter": {
                                    "term": {
                                        "related_user": current_user_email
                                    }
                                }
                            })
            res = res['hits']['hits']
            task_param = {"pleb": request.user.email, "query_param":
                search_form.cleaned_data['query_param'],
                          "keywords": response['keywords']}
            spawn_task(task_func=update_search_query, task_param=task_param)
            if not res:
                html = render_to_string('search_result_empty.html')
                return Response({'html': html}, status=200)
            paginator = Paginator(res, display_num)
            try:
                page = paginator.page(page)
            except PageNotAnInteger:
                page = paginator.page(1)
            except EmptyPage:
                page = paginator.page(paginator.num_pages)
            if current_page == 1:
                pool = Pool(3)
                results = pool.map(process_search_result, page.object_list)
                print results
                results = sorted(results, key=itemgetter('temp_score'),
                                 reverse=True)
            elif current_page > 1:
                for item in page.object_list:
                    if item['_type'] == 'sb_questions.neo_models.SBQuestion':
                        results.append(prepare_question_search_html(
                            item['_source']['question_uuid']))
                        spawn_task(update_weight_relationship,
                                   task_param=
                                   {'index': item['_index'],
                                    'document_id': item['_id'],
                                    'object_uuid': item['_source'][
                                        'question_uuid'],
                                    'object_type': 'question',
                                    'current_pleb': item['_source'][
                                        'related_user'],
                                    'modifier_type': 'search_seen'})
                    if item['_type'] == 'pleb':
                        spawn_task(update_weight_relationship,
                            task_param={'index': item['_index'],
                                   'document_id': item['_id'],
                                   'object_uuid':
                                       item['_source']['pleb_email'],
                                   'object_type': 'pleb',
                                   'current_pleb': item['_source'][
                                       'related_user'],
                                   'modifier_type': 'search_seen'})
                        results.append(prepare_user_search_html(
                            item['_source']['pleb_email']))
            try:
                next_page_num = page.next_page_number()
            except EmptyPage:
                next_page_num = ""
            return Response({'html': results, 'next': next_page_num}, status=200)
        except Exception:
            logger.exception(dumps({"function": search_result_api.__name__,
                                    "exception": "Unhandled Exception"}))
            return Response({'detail': 'fail'}, status=400)
    else:
        print search_form.errors
        return Response({'detail': 'invalid form'}, status=400)
