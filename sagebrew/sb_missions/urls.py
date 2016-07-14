from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required

from sb_contributions.views import ContributionMissionView

from .views import (mission_redirect_page, mission_updates,
                    MissionSettingsView, MissionBaseView,
                    mission_edit_updates, mission_endorsements,
                    mission_account_signup)


urlpatterns = patterns(
    'sb_missions.views',
    # List
    url(r'^$', TemplateView.as_view(template_name="mission/list.html"),
        name='mission_list'),

    # Setup
    url(r'^select/$', login_required(
        TemplateView.as_view(template_name="mission/selector.html")),
        name="select_mission"),
    url(r'^public_office/$', login_required(
        TemplateView.as_view(template_name="mission/public_office.html")),
        name="public_office"),
    url(r'^advocate/$', login_required(
        TemplateView.as_view(template_name="mission/advocate.html")),
        name="advocate"),
    url(r'^account/$', mission_account_signup, name="account_setup"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/$',
        mission_redirect_page, name="mission_redirect"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/review/$',
        TemplateView.as_view(template_name="manage/submit_for_review.html"),
        name='submit_mission_for_review'),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'finish_epic/$',
        TemplateView.as_view(template_name="manage/must_finish_epic.html"),
        name='must_finish_epic'),

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
        MissionSettingsView.as_view(template_name='updates/create.html'),
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
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'manage/gifts/$',
        MissionSettingsView.as_view(
            template_name='manage/mission_gifts.html'),
        name="mission_gifts"),

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
