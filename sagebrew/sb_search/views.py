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

from neomodel import DoesNotExist, CypherException

from .tasks import update_search_query
from .utils import process_search_result
from .forms import SearchForm, SearchFormApi
from api.alchemyapi import AlchemyAPI
from api.utils import (spawn_task)
from plebs.neo_models import Pleb
from plebs.utils import prepare_user_search_html
from sb_search.tasks import (spawn_weight_relationships)
from sb_questions.utils import prepare_question_search_html
from sb_registration.utils import verify_completed_registration
from sb_public_official.utils import prepare_official_search_html



@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def search_result_view(request):
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
    # TODO Need to make sure responses return an actual page if necessary
    try:
        pleb = Pleb.nodes.get(email=request.user.email)
    except(Pleb.DoesNotExist, DoesNotExist):
        return Response(status=404)
    except CypherException:
        return Response(status=500)
    query_param = request.GET.get('q', "")
    page = request.GET.get('page', 1)
    search_filter = request.GET.get('filter', 'general')
    display_num = request.GET.get('max_page_size', 10)
    if int(display_num) > 100:
        display_num = 100
    search_data = {'query_param': query_param, 'page': page, 'display_num':
                   display_num}
    search_form = SearchForm(search_data)
    if search_form.is_valid():
        return render(request, 'search.html',
                      {'search_param': search_form.cleaned_data['query_param'],
                       'page': search_form.cleaned_data['page'],
                       'pleb_info': pleb, 'filter': search_filter},
                      status=200)
    else:
        return render(request, 'search.html', {'pleb_info': pleb},status=400)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def search_result_api(request):
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
    # TODO Make sure calling function knows what to do with a 500 status
    # TODO can we move any of this into a util?
    query_param = request.query_params.get('q', "")
    page = request.query_params.get('page', 1)
    filter_type = request.query_params.get('filter', 'general')
    display_num = request.GET.get('max_page_size', 10)
    if int(display_num) > 100:
        display_num = 100
    data = {'query_param': query_param, 'display_num': display_num,
            'page': int(page), 'filter_param': filter_type}

    try:
        search_form = SearchFormApi(data)
        valid_form = search_form.is_valid()
    except AttributeError:
        # TODO Return something relevant
        return Response(status=400)
    if valid_form is True:
        search_type_dict = dict(settings.SEARCH_TYPES)
        alchemyapi = AlchemyAPI()
        response = alchemyapi.keywords("text", search_form.cleaned_data[
                                      'query_param'])
        current_page = int(search_form.cleaned_data['page'])
        results=[]
        current_user_email = request.user.email
        current_user_email,current_user_address = current_user_email.split('@')
        # TODO surround ES query with proper exception handling and ensure
        # each one is handled correctly
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        #TODO run query_param through natural language processor, determine
        #if what they have searched is an email address or a name so that
        #the first search result is that user
        #TODO implement filtering on auto generated keywords from alchemyapi
        if search_form.cleaned_data['filter_param'] == 'general':
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
        else:
            res = es.search(index='full-search-user-specific-1', size=50,
                            doc_type=search_type_dict[
                                search_form.cleaned_data['filter_param']],
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
        spawned = spawn_task(task_func=update_search_query,
                             task_param=task_param)
        if isinstance(spawned, Exception) is True:
            return Response({'detail': "server error"}, status=500)
        # TODO is this the correct way to check if res is empty? Seems to be
        # getting by this and attempting stuff further on down with no results
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
        res = spawn_task(task_func=spawn_weight_relationships,
                         task_param={'search_items': page.object_list})
        if isinstance(res, Exception) is True:
            # TODO Probably want to handle this differently
            return Response({'detail': 'server error'}, status=500)
        if current_page == 1:
            pool = Pool(3)
            try:
                results = pool.map(process_search_result, page.object_list)
            except RuntimeError:
                # TODO Might want to return something different here
                # Also if this is likely reocurring issue we might want to
                # look at an alternative process for it.
                # This seems to just be spawning off tasks too, could that
                # be spawned into a task of itself that manages spawning off
                # multiple tasks rather than Pool?
                return Response({'detail': "server error"}, status=500)
            results = sorted(results, key=itemgetter('temp_score'),
                             reverse=True)
        elif current_page > 1:
            for item in page.object_list:
                # TODO Can we generalize this any further?
                # TODO Handle spawned response correctly
                if item['_type'] == 'sb_questions.neo_models.SBQuestion':
                    results.append(prepare_question_search_html(
                        item['_source']['object_uuid']))
                elif item['_type'] == 'pleb':
                    results.append(prepare_user_search_html(
                        item['_source']['pleb_username']))
                elif item['_type'] == 'sagas':
                    results.append(prepare_official_search_html(
                        item['_source']['object_uuid']))
        try:
            next_page_num = page.next_page_number()
        except EmptyPage:
            next_page_num = ""
        return Response({'html': results, 'next': next_page_num},
                        status=200)
    else:
        return Response({'detail': 'invalid form'}, status=400)
