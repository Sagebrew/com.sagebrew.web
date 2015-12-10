from django.conf.urls import patterns, url

from .views import (saga, edit_epic, insights, moderators, quest)

urlpatterns = patterns(
    'sb_public_official.views',
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/$', quest,
        name='quest'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/$', saga,
        name='quest_saga'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/insights/$', insights,
        name='quest_stats'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/moderators/$', moderators,
        name='quest_moderators'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/edit_epic/$', edit_epic,
        name="quest_epic")
)
