from django.conf.urls import patterns, url

from .views import search_result_view, search_view, test

urlpatterns = patterns(
    'sb_search.views',
    url(r'^$', search_view, name="search"),
    url(r'^q=(?P<query_param>[A-Za-z0-9.@_%+-]{1,100})', search_result_view, name="search_results"),
    url(r'^test/$', test, name="test"),
)