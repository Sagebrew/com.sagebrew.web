from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^admin_council/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What's the Admin Council and how do I get on it?",
            "description": "The Admin Council is one of the most distinguished "
                           "bodies on Sagebrew. This article details some of "
                           "their responsibilities and what it takes to join "
                           "its ranks.",
            "content_path":
                "%s/static/rendered_docs/admin_council.html" % (
                    settings.STATIC_URL)
        },
        name="admin_council"),
    url(r'^reputation_changed_user_removed/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": 'Why do I have a reputation change on my reputation page '
                     'that says "User was removed"?',
            "description": "It's unfortunate but some users abuse the system. "
                           "This sometimes affects innocent bystander's, we're"
                           "sorry you were one of them.",
            "content_path":
                "%s/static/rendered_docs/reputation_change_user_remove.html" % (
                    settings.STATIC_URL)
        },
        name="reputation_changed_user_removed"),
    url(r'^what_are_badges/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What are badges?",
            "description": "Reputation isn't the only puzzle piece that you "
                           "need to advance in Sagebrew. Badges are another "
                           "key component of distinguishing yourself.",
            "content_path":
                "%s/static/rendered_docs/what_are_badges.html" % (
                    settings.STATIC_URL)
        },
        name="what_are_badges"),
)