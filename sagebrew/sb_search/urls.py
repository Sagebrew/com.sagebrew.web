from django.conf.urls import patterns, url

from .views import search_result_view, search_view, search_result_api

urlpatterns = patterns(
    'sb_search.views',
    url(r'^$', search_view, name="search"),
    url(r'^api/(?P<query_param>.+?)/(?P<page>[0-9]{1,100})/(?P<filter_type>.+?)/$',
        search_result_api, name="search_result_api"),
    url(r'^(?P<query_param>.+?)/(?P<page>[0-9]{1,100})/(?P<search_filter>.+?)/$',
        search_result_view, name="search_results"),

)