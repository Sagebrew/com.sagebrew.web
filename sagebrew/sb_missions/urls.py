from django.conf.urls import patterns, url

from sb_contributions.views import ContributionMissionView

from .views import (public_office_mission, advocate_mission, select_mission,
                    mission_redirect_page, mission_updates,
                    MissionSettingsView, MissionBaseView, mission_list,
                    mission_edit_updates, mission_endorsements)


urlpatterns = patterns(
    'sb_missions.views',
    # List
    url(r'^$', mission_list, name='mission_list'),

    # Setup
    url(r'^select/$', select_mission, name="select_mission"),
    url(r'^public_office/$', public_office_mission,
        name="public_office"),
    url(r'^advocate/$', advocate_mission, name="advocate"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/$',
        mission_redirect_page, name="mission_redirect"),

    # Manage
    url(r'^settings/$', MissionSettingsView.as_view(),
        name="mission_settings_redirect"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'manage/general/$',
        MissionSettingsView.as_view(), name="mission_settings"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'manage/epic/$',
        MissionSettingsView.as_view(template_name='manage/epic.html'),
        name="mission_epic"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'manage/epic/edit/$',
        MissionSettingsView.as_view(template_name='manage/epic_edit.html'),
        name="mission_edit_epic"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'manage/updates/$',
        MissionSettingsView.as_view(template_name='manage/updates.html'),
        name="mission_update_settings"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'manage/updates/create/$',
        MissionSettingsView.as_view(template_name='manage/update_create.html'),
        name="mission_update_create"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'manage/updates/(?P<edit_id>[A-Za-z0-9.@_%+-]{36})/edit/$',
        mission_edit_updates,
        name="mission_edit_update"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'manage/insights/$',
        MissionSettingsView.as_view(
            template_name='manage/mission_insights.html'),
        name="mission_insights"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'manage/volunteers/$',
        MissionSettingsView.as_view(
            template_name='manage/mission_volunteers.html'),
        name="mission_volunteers"),

    # Donate
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'donate/amount/$', ContributionMissionView.as_view(
            template_name="donations/amount.html"),
        name="mission_donation_amount"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'donate/name/$',
        ContributionMissionView.as_view(template_name='donations/name.html'),
        name="mission_donation_name"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'donate/payment/$',
        ContributionMissionView.as_view(
            template_name='donations/payment.html'),
        name="mission_donation_payment"),

    # Volunteer
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'volunteer/option/$', ContributionMissionView.as_view(
            template_name="volunteer/volunteer.html"),
        name="mission_volunteer_option"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'volunteer/name/$',
        ContributionMissionView.as_view(template_name='volunteer/name.html'),
        name="mission_volunteer_name"),

    # Endorse
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'endorse/$',
        ContributionMissionView.as_view(template_name='mission/endorse.html'),
        name="mission_endorse"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'endorse/name/$',
        ContributionMissionView.as_view(
            template_name='mission/endorse_name.html'),
        name="mission_endorse_name"),

    # View
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/updates/$',
        mission_updates, name="mission_updates"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'endorsements/$',
        mission_endorsements, name="mission_endorsements"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/$',
        MissionBaseView.as_view(), name="mission"),
)
