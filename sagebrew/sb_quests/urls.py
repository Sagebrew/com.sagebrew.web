from django.conf.urls import patterns, url

from .views import (saga, edit_epic,
                    insights, moderators,
                    manage_settings, delete_quest)

urlpatterns = patterns(
    'sb_public_official.views',
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/$', saga,
        name='quest_saga'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/insights/$', insights,
        name='quest_stats'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/moderators/$', moderators,
        name='quest_moderators'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/epic/$', edit_epic,
        name="quest_epic"),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/$', manage_settings,
        name='quest_manage_settings'),
    url(r'^delete_quest/$', delete_quest, name="delete_quest"),

)
