from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView, RedirectView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^funding-not-in-account/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "I've reached my Goal but there are no funds in"
                     " my bank account",
            "description": "Sometimes there are issues with releasing funds."
                           " Have you provided an update for your last Goal?"
                           " There might be issues with your account "
                           "information. Contact us and we'll help figure it "
                           "out.",
            "content_path":
                "%sfunding_not_in_account.html" % settings.HELP_DOCS_PATH,
            "category": "quest"
    },
        name="funding_not_in_account"),
    url(r'^how-to-export-contributions/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "I need to file the contributions to my campaign",
            "description": "Short description of how representatives can export"
                           " the information associated with the the "
                           "contributions they've received.",
            "content_path":
                "%show_export_contributions.html" % settings.HELP_DOCS_PATH,
            "category": "quest"
    },
        name="how_to_export_contributions"),
    url(r'^how-to-get-on-the-ballot/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How do I get my name on the ballot?",
            "description": "Brief explanation on how a candidate goes about "
                           "getting their name on the ballot.",
            "content_path":
                "%show_to_get_name_on_ballot.html" % settings.HELP_DOCS_PATH,
            "category": "quest"
    },
        name="how_to_get_on_the_ballot"),
    url(r'^how-to-run/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How to run for office",
            "description": "Information on what you need to know if you "
                           "want to run for public office.",
            "content_path":
                "%show_to_run_for_office.html" % settings.HELP_DOCS_PATH,
            "category": "quest"
    },
        name="how_to_run"),
    url(r'^name-on-ballot-to-run/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Do I have to have my name on the ballot to run for "
                     "federal office?",
            "description": "Many candidates may wonder if they need to have "
                           "their name on the ballot to run for office. This "
                           "article provides an solution to that question.",
            "content_path":
                "%sname_on_ballot_to_run.html" % settings.HELP_DOCS_PATH,
            "category": "quest"
    },
        name="name_on_ballot_to_run"),
    url(r'^need-more-help-public-official/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What if I need more help",
            "description": "Getting more help is just a click away, please"
                           " let us know what you need assistance with!",
            "content_path":
                "%sneed_more_help_repsagetribune.html" % (
                    settings.HELP_DOCS_PATH),
            "category": "quest"
    },
        name="need_more_help_repsagetribune"),
    url(r'^principal-campaign-committee/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What is a principal campaign committee?",
            "description": "This is your campaign team.",
            "content_path":
                "%swhat_is_principle_campaign_committee.html" % (
                    settings.HELP_DOCS_PATH),
            "category": "quest"
    },
        name="principle_campaign_committee"),
    url(r'^quest/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Embarking on a Quest",
            "description": "Quests are for anyone looking to run for public "
                           "office. We know running a campaign is hard work"
                           " and we're here to help you along your journey!",
            "content_path":
                "%squest_signup.html" % settings.HELP_DOCS_PATH,
            "category": "quest",
            "static_files": True
    },
        name="quest_signup"),
    url(r'^funding_not_in_account/$', RedirectView.as_view(
        url='/help/quest/funding-not-in-account/', permanent=True),
        name='funding_not_in_account_redirect'),
    url(r'^how_to_export_contributions/$', RedirectView.as_view(
        url='/help/quest/how-to-export-contributions/', permanent=True),
        name='how_to_export_contributions_redirect'),
    url(r'^how_to_get_on_the_ballot/$', RedirectView.as_view(
        url='/help/quest/how-to-get-on-the-ballot/', permanent=True),
        name='how_to_get_on_the_ballot_redirect'),
    url(r'^how_to_run/$', RedirectView.as_view(
        url='/help/quest/how-to-run/', permanent=True),
        name='how_to_run_redirect'),
    url(r'^name_on_ballot_to_run/$', RedirectView.as_view(
        url='/help/quest/name-on-ballot-to-run/', permanent=True),
        name='name_on_ballot_to_run_redirect'),
    url(r'^need_more_help_public_official/$', RedirectView.as_view(
        url='/help/quest/need-more-help-public-official/', permanent=True),
        name='need_more_help_public_official_redirect'),
    url(r'^principal_campaign_committee/$', RedirectView.as_view(
        url='/help/quest/principal-campaign-committee/', permanent=True),
        name='principal_campaign_committee_redirect'),
)
