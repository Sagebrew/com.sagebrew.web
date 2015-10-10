from django.conf.urls import patterns, url

from .views import (get_search_html)

urlpatterns = patterns(
    'sb_public_official.views',
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{2,36})/search/', get_search_html,
        name="rep_search_html")
)
