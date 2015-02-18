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
    url(r'^conceding/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What happens if I concede to another solution?",
            "description": "The goal is always to find the best solution that "
                           "has the greatest outcome for the largest group of "
                           "people. Conceding allows for the community to "
                           "focus in on the top solutions.",
            "content_path":
                "%s/static/rendered_docs/conceding.html" % (
                    settings.STATIC_URL)
        },
        name="conceding"),
    url(r'^moderators/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Who are the site moderators, and what is their role "
                     "here?",
            "description": "Moderators are members of the Admin Council, the "
                           "elders of the Sagebrew community who are tasked "
                           "with keeping Sagebrew running fluidly.",
            "content_path":
                "%s/static/rendered_docs/moderators.html" % (
                    settings.STATIC_URL)
        },
        name="moderators"),
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
    url(r'^serial_voting_change/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": 'Why do I have a reputation change on my reputation '
                     'page that says "serial Upvoting/Downvoting reversed"?',
            "description": "Some individuals abuse their privileges and affect "
                           "members of the community in a negative way. We "
                           "are sorry that this happens and do all we can to "
                           "hinder abuse and reprimand those who misuse the "
                           "system while trying to limit the impact it has on "
                           "our members.",
            "content_path":
                "%s/static/rendered_docs/serial_voting_change.html" % (
                    settings.STATIC_URL)
        },
        name="serial_voting_change"),
    url(r'^user_removed_change/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": 'Why do I have a reputation change on my reputation page '
                     'that says "User was removed"?',
            "description": "Some individuals abuse their privileges and affect "
                           "members of the community in a negative way. We "
                           "are sorry that this happens and do all we can to "
                           "hinder abuse and reprimand those who misuse the "
                           "system while trying to limit the impact it has on "
                           "our members.",
            "content_path":
                "%s/static/rendered_docs/user_removed_change.html" % (
                    settings.STATIC_URL)
        },
        name="user_removed_change"),
    url(r'^voting_importance/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": 'Why is voting on Questions, Solutions, and Comments '
                     'important?',
            "description": "Voting provides helpful feedback and allows the "
                           "community at large to see which ideas are the "
                           "most popular and the most encompassing",
            "content_path":
                "%s/static/rendered_docs/voting_importance.html" % (
                    settings.STATIC_URL)
        },
        name="voting_importance"),
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
    url(r'^$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What is Reputation? How do I earn (and lose) it?",
            "description": "Reputation is one of the ways the community can "
                           "gauge the knowledge and wit of a fellow member.",
            "content_path":
                "%s/static/rendered_docs/reputation.html" % (
                    settings.STATIC_URL)
        },
        name="reputation"),
)