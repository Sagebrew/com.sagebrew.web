from os import environ

from django.conf.urls import include
from django.conf import settings
from django.contrib import admin
from django.views.generic.base import TemplateView, RedirectView
from django.conf.urls import patterns, url

from sb_registration.views import (login_view, logout_view, signup_view,
                                   beta_page)

urlpatterns = patterns(
    '',
    (r'^favicon.ico$', RedirectView.as_view(url="%sfavicon.ico" % (
        settings.STATIC_URL))),
    url(r'^login/$', login_view, name="login"),
    url(r'^logout/$', logout_view, name="logout"),
    url(r'^password_reset/', 'django.contrib.auth.views.password_reset',
        {"html_email_template_name": "email_templates/email_password_reset.html"}),
    url(r'^password_reset/done/$',
        'django.contrib.auth.views.password_reset_done',
        name="password_reset_done"),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm', name="password_reset_confirm"),
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete', name="password_reset_complete"),
    url(r'^terms/$',  RedirectView.as_view(
        url='/help/terms/', permanent=False),name='terms_redirect'),
    url(r'^404/$', TemplateView.as_view(template_name="404.html"),
        name="404_Error"),
    (r'^contact_us/$', TemplateView.as_view(template_name="contact_us.html")),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    (r'^registration/', include('sb_registration.urls')),
    (r'^help/', include('help_center.urls')),
    (r'^comments/', include('sb_comments.urls')),
    (r'^posts/', include('sb_posts.urls')),
    (r'^notifications/', include('sb_notifications.urls')),
    (r'^relationships/', include('sb_relationships.urls')),
    (r'^user/', include('plebs.urls')),
    (r'^conversations/', include('sb_questions.urls')),
    (r'^solutions/', include('sb_answers.urls')),
    (r'^badges/', include('sb_badges.urls')),
    (r'^search/', include('sb_search.urls')),
    (r'^tags/', include('sb_tag.urls')),
    (r'^flag/', include('sb_flags.urls')),
    (r'^vote/', include('sb_votes.urls')),
    (r'^edit/', include('sb_edits.urls')),
    (r'^delete/', include('sb_deletes.urls')),
    (r'^docstore/', include('sb_docstore.urls')),
    (r'^reps/', include('sb_reps.urls')),
    (r'^upload/', include('sb_uploads.urls')),
    (r'^privilege/', include('sb_privileges.urls')),
    (r'^action/', include('sb_public_official.urls')),
    url(r'^signup/$', signup_view, name="signup"),
    url(r'^$', beta_page, name='beta_page'),
)

if settings.DEBUG is True:
    urlpatterns += patterns(
        (r'^admin/', include('admin_honeypot.urls')),
        (r'^secret/', include(admin.site.urls))
    )

if environ.get("CIRCLE_BRANCH", "") == "staging" and settings.DEBUG is False:
    urlpatterns += patterns(
        (r'^admin/', include('admin_honeypot.urls')),
        (r'^secret/', include(admin.site.urls)),
        (r'^robots.txt$', RedirectView.as_view(url="%srobots_staging.txt" % (
            settings.STATIC_URL))),
    )
else:
    urlpatterns += patterns(
        (r'^robots.txt$', RedirectView.as_view(url="%srobots.txt" % (
            settings.STATIC_URL))),
    )