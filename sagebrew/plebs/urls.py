from django.conf.urls import patterns, url

from .views import (get_user_search_view, ProfileView,
                    deactivate_user, root_profile_page, general_settings,
                    quest_settings)

urlpatterns = patterns(
    'plebs.views',
    url(r'^settings/$', general_settings, name="general_settings"),
    url(r'^quest_settings/$', quest_settings, name="quest_settings"),
    url(r'^deactivate_user/$', deactivate_user, name="deactivate_user"),
    url(r'^(?P<pleb_username>[A-Za-z0-9.@_%+-]{1,30})/friends/$',
        ProfileView.as_view(template_name='sb_friends_section/sb_friends.html'),
        name="friend_page"),
    url(r'^(?P<pleb_username>[A-Za-z0-9.@_%+-]{1,30})/$',
        ProfileView.as_view(), name="profile_page"),
    url(r'^search/(?P<pleb_username>[A-Za-z0-9.@_%+-]{1,30})/$',
        get_user_search_view, name="get_user_search_view"),
    url(r'^', root_profile_page, name="root_profile_page"),
)
