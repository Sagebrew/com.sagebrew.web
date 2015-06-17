from django.conf.urls import patterns, url

from .views import (saga, updates, get_search_html, edit_epic)

urlpatterns = patterns(
    'sb_public_official.views',
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{1,36})/$', saga,
        name='quest_saga'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{1,36})/updates/', updates,
        name='quest_updates'),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{1,36})/search/', get_search_html,
        name="rep_search_html"),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{1,36})/edit_epic/', edit_epic,
        name="quest_epic"),
)
