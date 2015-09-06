from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^after_donating_to_a_candidate/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What happens when I donate to a Candidate?",
            "description": "There are a couple events that occur after you "
                           "donate to a Candidate. This article explains what"
                           " they are.",
            "content_path":
                "%safter_donating_to_a_candidate.html" % (
                    settings.HELP_DOCS_PATH),
            "category": "citizens"
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
                "%sdonating_to_a_candidate.html" % settings.HELP_DOCS_PATH,
            "category": "citizens"
        },
        name="donating_to_a_candidate"),
    url(r'^goals/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What are Goals?",
            "description": "Goals are a way for a candidate running"
                           " for office to fundraise and organize their "
                           "campaign goals.",
            "content_path":
                "%sdonation_goals_citizen.html" % settings.HELP_DOCS_PATH,
            "category": "citizens"
        },
        name="donation_goals_citizen"),
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
                "%spledging_votes.html" % settings.HELP_DOCS_PATH,
            "category": "citizens"
        },
        name="pledging_votes"),
    url(r'^contributions/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why we think you should pledge a vote for your "
                     "Representative",
            "description": "There are rules and regulations in place when it "
                           "comes to donating money to a political campaign. "
                           "These rules and regulations are set in an effort to"
                           " keep campaigning fair and to place a barrier "
                           "between money and political sway. The basic "
                           "contribution limits are detailed here.",
            "content_path":
                "%scampaign_contribution_rules.html" % (
                    settings.HELP_DOCS_PATH),
            "category": "citizens"
        },
        name="campaign_contribution_rules"),
    url(r'^quest/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What is a Quest?",
            "description": "A Quest is a space for those who wish to "
                           "run for office to showcase themselves to the "
                           "constituency.",
            "content_path":
                "%saction_area_citizen.html" % (
                    settings.HELP_DOCS_PATH),
            "category": "citizens"
        },
        name="quest_citizen"),
)
