from django.conf.urls import patterns, url

from .views import (profile_information, interests, profile_picture, profile_page)


urlpatterns = patterns('sb_registration.views',
    url(r'^profile_information/$', profile_information, name="profile_info"),
    url(r'^interests/$', interests, name="interests"),
    url(r'^profile_picture/$', profile_picture, name="profile_picture"),
    url(r'^profile_page/$', profile_page, name="profile_page")
)
