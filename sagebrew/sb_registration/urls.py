from django.conf.urls import patterns, url

from .views import (profile_information, interests, invite_friends, auth_return, profile_picture)


urlpatterns = patterns('sb_registration.views',
    url(r'^profile_information/$', profile_information, name="profile_info"),
    url(r'^interests/$', interests, name="interests"),
    url(r'^invite_friends/$', invite_friends, name="invite_friends"),
    url(r'^profile_picture/$', profile_picture, name="profile_picture"),
    (r'^oauth2callback/$', auth_return),
)
