import traceback
from elasticsearch import Elasticsearch
from django.conf import settings
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.response import Response

from .forms import SearchForm
from api.utils import (get_post_data, post_to_garbage,
                       spawn_task)
from plebs.neo_models import Pleb
from sb_search.tasks import update_weight_relationship

@login_required()
def search_view(request):
    return render(request, 'search_page.html', {})

@login_required()
def search_result_view(request, query_param, display_num=5, page=1,
                       range_start=0, range_end=10):
    search_data = {'query_param': query_param, 'page': page}
    search_form = SearchForm(search_data)
    if search_form.is_valid():
        return render(request, 'search_result.html',
                      {'search_param': search_form.cleaned_data['query_param'],
                       'page': search_form.cleaned_data['page']})
    else:
        print search_form.errors
        return render(request, 'search_result.html')


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def search_result_api(request, query_param="", display_num=5, page=1,
                      filter_type="", filter_param=""):
    print
    html_array=[]
    try:
        html=""
        es = Elasticsearch(settings.ELASTIC_URL)
        res = es.search(index='full-search', from_=0, size=25, suggest_text=True, body={
                "query": {
                    "filtered": {
                        "query": {
                            "query_string": {
                                "query": query_param
                            }
                        },
                        "filter": {
                        }
                    }
                }
            })
        res = res['hits']['hits']
        if not res:
            html = render_to_string('search_result_empty.html')
            return Response({'html': html}, status=200)
        for item in res:
            item['score'] = item.pop('_score')
            item['type'] = item.pop('_type')
            item['source'] = item.pop('_source')
        paginator = Paginator(res, display_num)
        try:
            page = paginator.page(page)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        for item in page.object_list:
            if item['type'] == 'question':
                spawn_task(update_weight_relationship,
                           task_param={'object_uuid': item['source']['question_uuid'],
                                       'object_type': 'question',
                                       'current_pleb': request.user.email,
                                       'modifier_type': 'seen'})
                html_array.append(render_to_string('question_search_hidden.html', item))

        try:
            html_array.append(render_to_string('next_page.html',
                                               {'next_page': page.next_page_number()}))
        except EmptyPage:
            pass
        return Response({'html': html_array}, status=200)
    except Exception, e:
        traceback.print_exc()
        print e
        return Response({'detail': 'fail'}, status=400)
