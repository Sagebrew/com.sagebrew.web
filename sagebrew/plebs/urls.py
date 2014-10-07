from django.conf.urls import patterns, url

from .views import (profile_page, get_user_search_view,
                    about_page, friends_page,
                    reputation_page)


urlpatterns = patterns(
    'plebs.views',

    url(r'^(?P<pleb_email>[A-Za-z0-9.@_%+-]{7,40})/about/',
       about_page, name="about_page"),
    url(r'^(?P<pleb_email>[A-Za-z0-9.@_%+-]{7,40})/friends/',
       friends_page, name="friends_page"),
    url(r'^(?P<pleb_email>[A-Za-z0-9.@_%+-]{7,40})/reputation/',
       reputation_page, name="reputation_page"),
    url(r'^search/(?P<pleb_email>[A-Za-z0-9.@_%+-]{1,60})',
        get_user_search_view, name="get_user_search_view"),
    url(r'^(?P<pleb_email>[A-Za-z0-9.@_%+-]{7,60})/',
       profile_page, name="profile_page"),

)