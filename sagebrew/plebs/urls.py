from django.conf.urls import patterns, url

from .views import profile_page, get_user_search_view


urlpatterns = patterns(
    'plebs.views',
    url(r'^search/(?P<pleb_email>[A-Za-z0-9.@_%+-]{1,40})', get_user_search_view,
        name="get_user_search_view"),
    url(r'^(?P<pleb_email>[A-Za-z0-9.@_%+-]{7,40})/',
       profile_page, name="profile_page"),

)