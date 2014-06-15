from django.conf.urls import patterns, url

from .views import (profile_information, interests)


urlpatterns = patterns('sb_registration.views',
    url(r'^profile_information/$', profile_information),
    url(r'^interests/$', interests),
)
