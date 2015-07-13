from os import environ

from django.conf.urls import include
from django.conf import settings
from django.contrib import admin
from django.views.generic.base import TemplateView, RedirectView
from django.conf.urls import patterns, url

from sb_registration.views import (login_view, logout_view, signup_view,
                                   beta_page, quest_signup)
from sb_registration.forms import CustomPasswordResetForm


urlpatterns = patterns(
    '',
    (r'^favicon.ico$', RedirectView.as_view(url="%sfavicon.ico" % (
        settings.STATIC_URL), permanent=True)),
    url(r'^login/$', login_view, name="login"),
    url(r'^logout/$', logout_view, name="logout"),
    url(r'^password_reset/', 'django.contrib.auth.views.password_reset',
        {
            "html_email_template_name":
                "email_templates/email_password_reset.html",
            "template_name": "password_reset/password_reset.html",
            "password_reset_form": CustomPasswordResetForm
        }, name="reset_password_page"),
    url(r'^password_reset/done/$',
        'django.contrib.auth.views.password_reset_done',
        name="password_reset_done"),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        {"template_name": "password_reset/password_change_form.html"},
        name="password_reset_confirm"),
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete',
        {"template_name": "password_reset/password_reset_done.html"},
        name="password_reset_complete"),
    url(r'^terms/$', RedirectView.as_view(
        url='/help/terms/', permanent=False), name='terms_redirect'),
    url(r'^400/$', TemplateView.as_view(template_name="400.html"),
        name="400_Error"),
    url(r'^404/$', TemplateView.as_view(template_name="404.html"),
        name="404_Error"),
    url(r'^500/$', TemplateView.as_view(template_name="500.html"),
        name="500_Error"),
    (r'^contact_us/$', TemplateView.as_view(template_name="contact_us.html")),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    (r'^registration/', include('sb_registration.urls')),
    (r'^help/', include('help_center.urls')),
    (r'^relationships/', include('plebs.relation_urls')),
    (r'^user/', include('plebs.urls')),
    (r'^conversations/', include('sb_questions.urls')),
    (r'^search/', include('sb_search.urls')),
    (r'^docstore/', include('sb_docstore.urls')),
    (r'^quests/', include('sb_public_official.urls')),
    (r'^council/', include('sb_council.urls')),
    (r'^updates/', include('sb_updates.urls')),
    url(r'^signup/$', signup_view, name="signup"),
    url(r'^quests/$', quest_signup, name='quest_info'),
    (r'^v1/', include('sb_questions.apis.v1')),
    (r'^v1/', include('sb_solutions.apis.v1')),
    (r'^v1/', include('sb_oauth.apis.v1')),
    (r'^v1/', include('plebs.apis.v1')),
    (r'^v1/', include('plebs.apis.beta_urls')),
    (r'^v1/', include('sb_posts.apis.v1')),
    (r'^v1/', include('sb_comments.apis.v1')),
    (r'^v1/', include('sb_flags.apis.v1')),
    (r'^v1/', include('sb_goals.apis.v1')),
    (r'^v1/', include('sb_votes.apis.v1')),
    (r'^v1/', include('sb_privileges.apis.v1')),
    (r'^v1/', include('sb_tags.apis.v1')),
    (r'^v1/', include('sb_updates.apis.v1')),
    (r'^v1/', include('sb_uploads.apis.v1')),
    (r'^v1/', include('sb_campaigns.apis.v1')),
    (r'^v1/', include('sb_donations.apis.v1')),
    (r'^v1/', include('sb_locations.apis.v1')),
    (r'^v1/', include('sb_council.apis.v1')),
    url(r'^$', beta_page, name='beta_page'),
)

if settings.DEBUG is True:
    urlpatterns += patterns(
        (r'^secret/', include(admin.site.urls)),
        (r'^robots.txt$', TemplateView.as_view(
            template_name='robots_staging.txt', content_type='text/plain')),
        (r'^loaderio-98182a198e035e1a9649f683fb42d23e/$', TemplateView.as_view(
            template_name='external_tests/loaderio.txt',
            content_type='text/plain')),
        (r'^14c08cb7770b778cba5856e49dbf24d3d8a2048e.html$',
         TemplateView.as_view(
             template_name='external_tests/'
                           '14c08cb7770b778cba5856e49dbf24d3d8a2048e.html',
             content_type='text/plain')),
    )
elif environ.get("CIRCLE_BRANCH", "") == "staging" and settings.DEBUG is False:
    urlpatterns += patterns(
        (r'^secret/', include(admin.site.urls)),
        (r'^robots.txt$', TemplateView.as_view(
            template_name='robots_staging.txt', content_type='text/plain')),
        (r'^loaderio-98182a198e035e1a9649f683fb42d23e/$', TemplateView.as_view(
            template_name='external_tests/loaderio.txt',
            content_type='text/plain')),
        (r'^14c08cb7770b778cba5856e49dbf24d3d8a2048e.html$',
         TemplateView.as_view(
             template_name='external_tests/'
                           '14c08cb7770b778cba5856e49dbf24d3d8a2048e.html',
             content_type='text/plain')),
    )
else:
    urlpatterns += patterns(
        (r'^robots.txt$', TemplateView.as_view(template_name='robots.txt',
                                               content_type='text/plain')),
    )
