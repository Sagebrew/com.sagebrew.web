from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from .views import (login_view_api, email_verification)


urlpatterns = patterns(
    'sb_registration.views',
    url(r'^signup/confirm/$', login_required(
        TemplateView.as_view(template_name='verify_email.html')),
        name="confirm_view"),
    # TODO should move this to pleb or sagebrew app
    url(r'^login/api/$', login_view_api, name="login_api"),
    url(r'^age_restriction/$', TemplateView.as_view(
        template_name='age_restriction_13.html'),
        name="age_restriction_13"),
    url(r'^email_confirmation/(?P<confirmation>[A-Za-z0-9.@_%+-]{24})/$',
        email_verification, name="email_verification")
)
