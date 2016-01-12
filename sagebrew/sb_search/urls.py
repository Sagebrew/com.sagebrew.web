from django.conf.urls import patterns, url

from .views import search_result_view

urlpatterns = patterns(
    'sb_search.views',
    url(r'^$', search_result_view, name="search_results"),
)
