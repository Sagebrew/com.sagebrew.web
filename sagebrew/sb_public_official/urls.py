from django.conf.urls import patterns, url

from .views import (saga, updates, get_search_html, edit_epic, create_update,
                    manage_goals, statistics, helpers)

urlpatterns = patterns(
    'sb_public_official.views',
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/$', saga,
        name='quest_saga'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/updates/', updates,
        name='quest_updates'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/statistics/', statistics,
        name='quest_stats'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/helpers/', helpers,
        name='quest_helpers'),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{2,36})/search/', get_search_html,
        name="rep_search_html"),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/edit_epic/', edit_epic,
        name="quest_epic"),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/create_update/',
        create_update, name="create_update"),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage_goals/',
        manage_goals, name="manage_goals")
)
