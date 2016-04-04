from django.conf.urls import patterns, url

from .views import (PersonalProfileView, ProfileView,
                    deactivate_user, root_profile_page, general_settings,
                    contribute_settings,
                    authenticate_representative, delete_account)

urlpatterns = patterns(
    'plebs.views',
    url(r'^settings/$', general_settings, name="general_settings"),
    url(r'^settings/delete/$', delete_account, name="settings_delete_account"),
    url(r'^settings/donations/$',
        PersonalProfileView.as_view(template_name='settings/donations.html'),
        name="donation_page"),
    url(r'^contribute/$', contribute_settings, name="contribute_settings"),
    url(r'^deactivate_user/$', deactivate_user, name="deactivate_user"),
    url(r'^authenticate_representative/$', authenticate_representative,
        name="auth_representative"),
    url(r'^newsfeed/$',
        PersonalProfileView.as_view(template_name='newsfeed.html'),
        name="newsfeed"),
    url(r'^(?P<pleb_username>[A-Za-z0-9.@_%+-]{1,30})/$',
        ProfileView.as_view(), name="profile_page"),
    url(r'^', root_profile_page, name="root_profile_page"),
)
