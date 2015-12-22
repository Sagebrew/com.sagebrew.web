from django.conf.urls import patterns, url

from .views import (insights, quest, delete_quest,
                    QuestSettingsView, saga)

urlpatterns = patterns(
    'sb_quests.views',
    # DEPRECATED
    url(r'^/deprecated/(?P<username>[A-Za-z0-9.@_%+-]{2,36})/$', saga,
        name='quest_saga'),

    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/$', quest, name='quest'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/insights/$', insights,
        name='quest_stats'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/moderators/$',
        QuestSettingsView.as_view(template_name="manage/moderators.html"),
        name='quest_moderators'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/banking/$',
        QuestSettingsView.as_view(template_name="manage/quest_banking.html"),
        name="quest_manage_banking"),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/billing/$',
        QuestSettingsView.as_view(template_name="manage/quest_billing.html"),
        name="quest_manage_billing"),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/add_payment/$',
        QuestSettingsView.as_view(template_name="manage/payment.html"),
        name="quest_add_payment"),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/delete/$',
        QuestSettingsView.as_view(template_name="manage/quest_delete.html"),
        name="quest_delete_page"),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/general/$',
        QuestSettingsView.as_view(), name='quest_manage_settings'),
    url(r'^delete_quest/$', delete_quest, name="delete_quest"),

)
