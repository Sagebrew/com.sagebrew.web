from django.conf.urls import patterns, url

from .views import (public_office_mission, advocate_mission, select_mission,
                    mission, mission_redirect_page, mission_updates,
                    edit_epic, mission_settings)


urlpatterns = patterns(
    'sb_missions.views',
    url(r'^select/$', select_mission, name="select_mission"),
    url(r'^public_office/$', public_office_mission,
        name="public_office_mission"),
    url(r'^advocate/$', advocate_mission, name="advocate_mission"),
    url(r'^mission_settings/$', mission_settings, name="mission_settings"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/$',
        mission_redirect_page, name="mission_redirect"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/$',
        mission, name="mission"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/updates/$',
        mission_updates, name="mission_updates"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/edit_epic/$',
        edit_epic, name="mission_edit_epic"),
)
