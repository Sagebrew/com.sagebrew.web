from django.conf.urls import patterns, url

from .views import search_result_view, search_view, search_result_api

urlpatterns = patterns(
    'sb_search.views',
    url(r'^$', search_view, name="search"),
    url(r'^q=(?P<query_param>.+?)&page=(?P<page>[0-9]{1,100})&filter=(?P<filter>[0-9]{1,100})$',
        search_result_view, name="search_results"),
    url(r'^api/q=(?P<query_param>.+?)&page=(?P<page>[0-9]{1,100})$',
        search_result_api, name="search_result_api"),
    url(r'^api/q=(?P<query_param>.+?)&page=(?P<page>[0-9]{1,100})&st=(?P<search_type>[A-Za-z0-9.@_%+-]{1,100})$',
        search_result_api, name="search_result_api"),
)