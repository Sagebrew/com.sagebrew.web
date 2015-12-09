from django.conf.urls import patterns, url

from .views import (public_office_mission, advocate_mission, select_mission)


urlpatterns = patterns(
    'sb_missions.views',
    url(r'^select/$', select_mission, name="select_mission"),
    url(r'^public_office/$', public_office_mission,
        name="public_office_mission"),
    url(r'^advocate/$', advocate_mission, name="advocate_mission"),
)
