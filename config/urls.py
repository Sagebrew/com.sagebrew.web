from os import environ

from django.conf.urls import include
from django.conf import settings
from django.contrib import admin
from django.views.generic.base import TemplateView, RedirectView
from django.conf.urls import url
from django.contrib.auth.views import (
    password_reset, password_reset_done, password_reset_confirm,
    password_reset_complete)
from django.contrib.sitemaps.views import sitemap

from sagebrew.sb_registration.views import (
    login_view, logout_view, signup_view,
    quest_signup, advocacy, political_campaign)
from sagebrew.plebs.sitemap import ProfileSitemap
from sagebrew.sb_questions.sitemap import QuestionSitemap
from sitemap import (StaticViewSitemap, SignupSitemap)
from sagebrew.sb_quests.sitemap import QuestSitemap
from sagebrew.sb_missions.sitemap import (
    MissionSitemap, MissionUpdateSitemap, MissionListSitemap)
from sagebrew.help_center.sitemap import (
    AccountHelpSitemap, ConversationHelpSitemap,
    DonationsHelpSitemap, PoliciesHelpSitemap,
    PrivilegeHelpSitemap, QuestHelpSitemap,
    QuestionHelpSitemap, ReputationModerationHelpSitemap,
    SecurityHelpSitemap, SolutionsHelpSitemap, TermsHelpSitemap)


urlpatterns = [
    url(r'^favicon\.ico$', RedirectView.as_view(url="%s/images/favicon.ico" % (
        settings.STATIC_URL), permanent=True)),
    url(r'^login/$', login_view, name="login"),
    url(r'^logout/$', logout_view, name="logout"),
    url(r'^password_reset/$', password_reset,
        {"template_name": "password_reset/password_reset.html"},
        name="reset_password_page"),
    url(r'^password_reset/done/$',
        password_reset_done, {
            "template_name": "password_reset/password_reset_sent.html"},
        name="password_reset_done"),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        password_reset_confirm,
        {"template_name": "password_reset/password_change_form.html"},
        name="password_reset_confirm"),
    url(r'^reset/done/$', password_reset_complete,
        {"template_name": "password_reset/password_reset_done.html"},
        name="password_reset_complete"),
    url(r'^terms/$', RedirectView.as_view(
        url='/help/terms/', permanent=False), name='terms_redirect'),
    url(r'^400/$', TemplateView.as_view(template_name="400.html"),
        name="400_Error"),
    url(r'^401/$', TemplateView.as_view(template_name="401.html"),
        name="401_Error"),
    url(r'^404/$', TemplateView.as_view(template_name="404.html"),
        name="404_Error"),
    url(r'^500/$', TemplateView.as_view(template_name="500.html"),
        name="500_Error"),
    url(r'^contact-us/$', RedirectView.as_view(
        url='/help/policies/support/', permanent=False),
        name='contact_us'),
    url(r'^contact_us/$', RedirectView.as_view(
        url='/contact-us/', permanent=True),
        name='contact_us_redirect'),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^registration/', include('sagebrew.sb_registration.urls')),
    url(r'^help/', include('sagebrew.help_center.urls')),
    url(r'^user/', include('sagebrew.plebs.urls')),
    url(r'^conversations/', include('sagebrew.sb_questions.urls')),
    url(r'^search/', include('sagebrew.sb_search.urls')),
    url(r'^quests/', include('sagebrew.sb_public_official.urls')),
    url(r'^quests/', include('sagebrew.sb_quests.urls')),
    url(r'^missions/', include('sagebrew.sb_missions.urls')),
    url(r'^council/', include('sagebrew.sb_council.urls')),
    url(r'^posts/', include('sagebrew.sb_posts.urls')),
    url(r'^solutions/', include('sagebrew.sb_solutions.urls')),
    url(r'^questions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/',
        TemplateView.as_view(template_name="single_object.html"),
        name="single_question_page"),
    url(r'^sitemap\.xml$', sitemap,
        {'sitemaps': {
            'questions': QuestionSitemap,
            'profiles': ProfileSitemap,
            'quests': QuestSitemap,
            'missions': MissionSitemap,
            'mission_list': MissionListSitemap,
            'updates': MissionUpdateSitemap,
            'static_pages': StaticViewSitemap,
            'sign_up': SignupSitemap,
            'account_help': AccountHelpSitemap,
            'conversation_help': ConversationHelpSitemap,
            'donation_help': DonationsHelpSitemap,
            'policy_help': PoliciesHelpSitemap,
            'privilege_help': PrivilegeHelpSitemap,
            'quest_help': QuestHelpSitemap,
            'question_help': QuestionHelpSitemap,
            'reputation_moderation_help': ReputationModerationHelpSitemap,
            'security_help': SecurityHelpSitemap,
            'solutions_help': SolutionsHelpSitemap,
            'terms_help': TermsHelpSitemap
        }},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^quest/$', quest_signup, name='quest_info'),
    url(r'^v1/', include('sagebrew.sb_questions.apis.v1')),
    url(r'^v1/', include('sagebrew.sb_solutions.apis.v1')),
    url(r'^v1/', include('sagebrew.sb_oauth.apis.v1')),
    url(r'^v1/', include('sagebrew.plebs.apis.v1')),
    url(r'^v1/', include('sagebrew.sb_address.apis.v1')),
    url(r'^v1/', include('sagebrew.sb_posts.apis.v1')),
    url(r'^v1/', include('sagebrew.sb_comments.apis.v1')),
    url(r'^v1/', include('sagebrew.sb_news.apis.v1')),
    url(r'^v1/', include('sagebrew.sb_missions.apis.v1')),
    url(r'^v1/', include('sagebrew.sb_privileges.apis.v1')),
    url(r'^v1/', include('sagebrew.sb_tags.apis.v1')),
    url(r'^v1/', include('sagebrew.sb_updates.apis.v1')),
    url(r'^v1/', include('sagebrew.sb_uploads.apis.v1')),
    url(r'^v1/', include('sagebrew.sb_quests.apis.v1')),
    url(r'^v1/', include('sagebrew.sb_donations.apis.v1')),
    url(r'^v1/', include('sagebrew.sb_locations.apis.v1')),
    url(r'^v1/', include('sagebrew.sb_council.apis.v1')),
    url(r'^v1/', include('sagebrew.sb_search.apis.v1')),
    url(r'^v1/', include('sagebrew.sb_accounting.apis.v1')),
    url(r'^v1/', include('sagebrew.sb_orders.apis.v1')),
    url(r'^advocacy/$', advocacy, name="advocacy"),
    url(r'^political/$', political_campaign, name="political"),
    url(r'^$', signup_view, name="signup"),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        url(r'^robots\.txt$', TemplateView.as_view(
            template_name='robots_staging.txt', content_type='text/plain')),
        url(r'^loaderio-98182a198e035e1a9649f683fb42d23e/$', TemplateView.as_view(
            template_name='external_tests/loaderio.txt',
            content_type='text/plain')),
        url(r'^14c08cb7770b778cba5856e49dbf24d3d8a2048e.html$',
         TemplateView.as_view(
             template_name='external_tests/'
                           '14c08cb7770b778cba5856e49dbf24d3d8a2048e.html',
             content_type='text/plain')),
        url(r'^secret/', include(admin.site.urls)),
    ]
elif environ.get("CIRCLE_BRANCH", "") == "staging" and settings.DEBUG is False:
    urlpatterns += [
        url(r'^robots\.txt$', TemplateView.as_view(
            template_name='robots_staging.txt', content_type='text/plain')),
        url(r'^loaderio-98182a198e035e1a9649f683fb42d23e/$',
            TemplateView.as_view(
                template_name='external_tests/loaderio.txt',
                content_type='text/plain')),
        url(r'^14c08cb7770b778cba5856e49dbf24d3d8a2048e.html$',
            TemplateView.as_view(
                template_name='external_tests/'
                              '14c08cb7770b778cba5856e49dbf24d3d8a2048e.html',
                content_type='text/plain')),
        url(r'^secret/', include(admin.site.urls)),
    ]
else:
    urlpatterns += [
        url(r'^robots\.txt$', TemplateView.as_view(
            template_name='robots.txt', content_type='text/plain')),
        url(r'^d667e6bf-d0fe-4aef-8efe-1e50c18b2aec/',
            include(admin.site.urls)),
    ]
