from django.conf.urls import patterns, url

from .views import (get_user_search_view, ProfileView,
                    deactivate_user, root_profile_page, general_settings,
                    quest_settings, contribute_settings,
                    delete_quest, authenticate_representative)

urlpatterns = patterns(
    'plebs.views',
    url(r'^settings/$', general_settings, name="general_settings"),
    url(r'^quest_settings/$', quest_settings, name="quest_settings"),
    url(r'^contribute/$', contribute_settings, name="contribute_settings"),
    url(r'^deactivate_user/$', deactivate_user, name="deactivate_user"),
    url(r'^delete_quest/$', delete_quest, name="delete_quest"),
    url(r'^authenticate_representative/$', authenticate_representative,
        name="auth_representative"),
    url(r'^newsfeed/$',
        ProfileView.as_view(template_name='newsfeed.html'), name="newsfeed"),
    url(r'^(?P<pleb_username>[A-Za-z0-9.@_%+-]{1,30})/friends/$',
        ProfileView.as_view(template_name='sb_friends_section/sb_friends.html'),
        name="friend_page"),
    url(r'^(?P<pleb_username>[A-Za-z0-9.@_%+-]{1,30})/photos/$',
        ProfileView.as_view(template_name='pleb_image_upload.html'),
        name='pleb_images'),
    url(r'^(?P<pleb_username>[A-Za-z0-9.@_%+-]{1,30})/$',
        ProfileView.as_view(), name="profile_page"),
    url(r'^search/(?P<pleb_username>[A-Za-z0-9.@_%+-]{1,30})/$',
        get_user_search_view, name="get_user_search_view"),
    url(r'^', root_profile_page, name="root_profile_page"),
)
