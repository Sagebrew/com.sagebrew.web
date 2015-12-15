from django.conf.urls import patterns, url

from .views import (insights, moderators, quest_list,
                    quest, manage_settings, delete_quest,
                    quest_delete_page, quest_manage_banking)

urlpatterns = patterns(
    'sb_public_official.views',
    url(r'^quests$', quest_list,
        name='quest_list'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/$', quest,
        name='quest'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/insights/$', insights,
        name='quest_stats'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/moderators/$',
        moderators, name='quest_moderators'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/banking/$',
        quest_manage_banking, name="quest_manage_banking"),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/delete/$',
        quest_delete_page, name="quest_delete_page"),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/$', manage_settings,
        name='quest_manage_settings'),
    url(r'^delete_quest/$', delete_quest, name="delete_quest"),

)
