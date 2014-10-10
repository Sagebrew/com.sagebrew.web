from django.conf.urls import patterns, url

from .views import (profile_information, interests, profile_picture,
                    signup_view, signup_view_api, login_view, logout_view,
                    login_view_api, email_verification, confirm_view,
                    resend_email_verification)


urlpatterns = patterns(
    'sb_registration.views',
    url(r'^$', signup_view, name="signup"),
    url(r'^signup/$', signup_view_api, name="signup_api"),
    url(r'^signup/confirm/$', confirm_view, name="confirm_view"),
    url(r'^login/api/$', login_view_api, name="login_api"),
    url(r'^profile_information/$', profile_information, name="profile_info"),
    url(r'^interests/$', interests, name="interests"),
    url(r'^profile_picture/$', profile_picture, name="profile_picture"),
    url(r'^email_confirmation/resend/$', resend_email_verification,
        name="resend_verification"),
    url(r'^email_confirmation/(?P<confirmation>[A-Za-z0-9.@_%+-]{24})/$',
        email_verification, name="email_verification")
)
