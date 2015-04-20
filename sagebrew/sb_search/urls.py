from django.conf.urls import patterns, url

from .views import search_result_view, search_result_api

urlpatterns = patterns(
    'sb_search.views',
    url(r'^api/$', search_result_api, name="search_result_api"),
    url(r'^$', search_result_view, name="search_results"),
)
