from django.conf.urls import url
from django.views.generic.base import TemplateView, RedirectView
from django.conf import settings


urlpatterns = [
    url(r'^admin-council/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What's the Admin Council and how do I get on it?",
            "description": "The Admin Council is one of the most distinguished "
                           "bodies on Sagebrew. This article details some of "
                           "their responsibilities and what it takes to join "
                           "its ranks.",
            "content_path":
                "%sadmin_council.html" % settings.HELP_DOCS_PATH,
            "category": "Reputation and Moderation"
    },
        name="admin_council"),

    url(r'^moderators/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Who are the site moderators, and what is their role "
                     "here?",
            "description": "Moderators are members of the Admin Council, the "
                           "elders of the Sagebrew community who are tasked "
                           "with keeping Sagebrew running fluidly.",
            "content_path":
                "%smoderators.html" % settings.HELP_DOCS_PATH,
            "category": "Reputation and Moderation"
    },
        name="moderators"),
    url(r'^reputation-changed-user-removed/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": 'Why do I have a reputation change on my reputation page '
                     'that says "User was removed"?',
            "description": "It's unfortunate but some users abuse the system. "
                           "This sometimes affects innocent bystander's, we're"
                           "sorry you were one of them.",
            "content_path":
                "%sreputation_change_user_remove.html" % (
                    settings.HELP_DOCS_PATH),
            "category": "Reputation and Moderation"
    },
        name="reputation_changed_user_removed"),
    url(r'^serial-voting-change/$', TemplateView.as_view(
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
                "%sserial_voting_change.html" % settings.HELP_DOCS_PATH,
            "category": "Reputation and Moderation"
    },
        name="serial_voting_change"),
    url(r'^user-removed-change/$', TemplateView.as_view(
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
                "%suser_removed_change.html" % settings.HELP_DOCS_PATH,
            "category": "Reputation and Moderation"
    },
        name="user_removed_change"),
    url(r'^voting-importance/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": 'Why is voting on Questions, Solutions, and Comments '
                     'important?',
            "description": "Voting provides helpful feedback and allows the "
                           "community at large to see which ideas are the "
                           "most popular and the most encompassing",
            "content_path":
                "%svoting_importance.html" % settings.HELP_DOCS_PATH,
            "category": "Reputation and Moderation"
    },
        name="voting_importance"),
    url(r'^$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What is Reputation? How do I earn (and lose) it?",
            "description": "Reputation is one of the ways the community can "
                           "gauge the knowledge and wit of a fellow member.",
            "content_path":
                "%sreputation.html" % settings.HELP_DOCS_PATH,
            "category": "Reputation and Moderation"
    },
        name="reputation"),
    url(r'^admin_council/$', RedirectView.as_view(
        url='/help/reputation/admin-council/', permanent=True),
        name='admin_council_redirect'),
    url(r'^reputation_changed_user_removed/$', RedirectView.as_view(
        url='/help/reputation/reputation-changed-user-removed/',
        permanent=True),
        name='reputation_changed_user_removed_redirect'),
    url(r'^serial_voting_change/$', RedirectView.as_view(
        url='/help/reputation/serial-voting-change/', permanent=True),
        name='serial_voting_change_redirect'),
    url(r'^user_removed_change/$', RedirectView.as_view(
        url='/help/reputation/user-removed-change/', permanent=True),
        name='user_removed_change_redirect'),
    url(r'^voting_importance/$', RedirectView.as_view(
        url='/help/reputation/voting-importance/', permanent=True),
        name='voting_importance_redirect'),
]
