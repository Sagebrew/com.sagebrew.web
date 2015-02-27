from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^after_donating_to_a_candidate/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What happens when I donate to a Candidate?",
            "description": "There a few options you have after you donate to "
                           "a candidate. This article outlines what they are.",
            "content_path":
                "%s/static/rendered_docs/after_donating_to_a_candidate.html" % (
                    settings.STATIC_URL)
        },
        name="after_donating_to_a_candidate"),
    url(r'^donating_to_a_candidate/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "I want to contribute to a candidate running for "
                     "office....Where do I begin?",
            "description": "Finding out information about candidates has never "
                           "been easier but you still need to do your research."
                           "If you have any questions please reach out to us.",
            "content_path":
                "%s/static/rendered_docs/donating_to_a_candidate.html" % (
                    settings.STATIC_URL)
        },
        name="donating_to_a_candidate"),
    url(r'^pledging_votes/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why we think you should pledge a vote for your "
                     "Representative",
            "description": "Pledging a vote gives encouragement to candidates "
                           "and helps them to gauge what their electability "
                           "is. Don't pledge a vote lightly, make sure the "
                           "candidate you give your vote to is who you will "
                           "actually vote for.",
            "content_path":
                "%s/static/rendered_docs/pledging_votes.html" % (
                    settings.STATIC_URL)
        },
        name="pledging_votes"),
)