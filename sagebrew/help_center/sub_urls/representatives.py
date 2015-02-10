from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^funding_not_in_account/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "I've reached my Donation Goal but there are no funds in"
                     " my bank account",
            "description": "Sometimes there are issues with releasing funds."
                           " Have you provided an update for your last Goal?"
                           " There might be issues with your account "
                           "information. Contact us and we'll help figure it "
                           "out.",
            "content_path":
                "%s/static/rendered_docs/funding_not_in_account.html" % (
                    settings.STATIC_URL)
        },
        name="funding_not_in_account"),
    url(r'^how_to_export_contributions/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "I need to file my contributions, how do I retrieve the "
                     "ones I received through Sagebrew?",
            "description": "Short description of how representatives can export"
                           " the information associated with the the "
                           "contributions they've received.",
            "content_path":
                "%s/static/rendered_docs/how_export_contributions.html" % (
                    settings.STATIC_URL)
        },
        name="how_to_export_contributions"),
    url(r'^how_to_get_on_the_ballot/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How do I get my name on the ballot?",
            "description": "Brief explanation on how a candidate goes about "
                           "getting their name on the ballot.",
            "content_path":
                "%s/static/rendered_docs/how_to_get_name_on_ballot.html" % (
                    settings.STATIC_URL)
        },
        name="how_to_get_on_the_ballot"),
    url(r'^name_on_ballot_to_run/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Do I have to have my name on the ballot to run for "
                     "federal office?",
            "description": "Many candidates may wonder if they need to have "
                           "their name on the ballot to run for office. This "
                           "article provides an answer to that question.",
            "content_path":
                "%s/static/rendered_docs/name_on_ballot_to_run.html" % (
                    settings.STATIC_URL)
        },
        name="name_on_ballot_to_run"),
)