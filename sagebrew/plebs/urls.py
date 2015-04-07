from django.conf.urls import patterns, url

from .views import (profile_page, get_user_search_view,
                    about_page, reputation_page, deactivate_user,
                    root_profile_page, general_settings)

urlpatterns = patterns(
    'plebs.views',
    url(r'^settings/$', general_settings, name="general_settings"),
    url(r'^deactivate_user/$', deactivate_user, name="deactivate_user"),
    url(r'^(?P<pleb_username>[A-Za-z0-9.@_%+-]{1,30})/$',
        profile_page, name="profile_page"),
    url(r'^(?P<pleb_username>[A-Za-z0-9.@_%+-]{1,30})/about/$',
        about_page, name="about_page"),
    url(r'^(?P<pleb_username>[A-Za-z0-9.@_%+-]{1,30})/reputation/$',
        reputation_page, name="reputation_page"),
    url(r'^search/(?P<pleb_username>[A-Za-z0-9.@_%+-]{1,30})/$',
        get_user_search_view, name="get_user_search_view"),

    url(r'^', root_profile_page, name="root_profile_page"),
)