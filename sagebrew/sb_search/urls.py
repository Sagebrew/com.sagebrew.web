from django.conf.urls import patterns, url

from .views import search_result_view, search_view

urlpatterns = patterns(
    'sb_search.views',
    url(r'^$', search_view, name="search"),
    url(r'^results/q=(?P<query_param>a-zA-Z0-9$', search_result_view, name="search_results"),
)