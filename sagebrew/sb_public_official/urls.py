from django.conf.urls import patterns, url

from .views import (saga, updates, get_search_html)

urlpatterns = patterns(
    'sb_questions.views',
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{1,36})/$', saga,
        name='action_saga'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{1,36})/updates/', updates,
        name='action_updates'),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{1,36})/search/', get_search_html,
        name="rep_search_html")
)
