from django.conf.urls import patterns, url

from .views import (profile_information, interests, invite_friends, auth_return)


urlpatterns = patterns('sb_registration.views',
    url(r'^profile_information/$', profile_information, name="profile_info"),
    url(r'^interests/$', interests, name="interests"),
    url(r'^invite_friends/$', invite_friends, name="invite_friends"),
    (r'^oauth2callback/$', auth_return),
)
