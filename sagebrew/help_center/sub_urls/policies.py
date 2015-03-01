from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^advertising/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Can I Advertise on Sagebrew?",
            "description": "We attempt to stay as neutral as possible and "
                           "believe allowing advertisement on the site would "
                           " hinder our credibility. We don't allow third "
                           "party advertising so that we ensure our focus stays"
                           " on our users and not those trying to exploit "
                           "them.",
            "content_path":
                "%sadvertising.html" % (settings.HELP_DOCS_PATH),
            "category": "policies"
        },
        name="advertising"),
    url(r'^be_nice/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Markdown Formatting",
            "description": "We try to foster a collaborative environment but "
                           "to do that we need the community to give us a "
                           "helping hand.",
            "content_path":
                "%sbe_nice.html" % (settings.HELP_DOCS_PATH),
            "category": "policies"
        },
        name="be_nice"),
    url(r'^do_not_spam/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How to not be a spammer",
            "description": "Some notes on what we consider a spammer and how "
                           "you can avoid being branded as one.",
            "content_path":
                "%sdont_spam.html" % (settings.HELP_DOCS_PATH),
            "category": "policies"
        },
        name="do_not_spam"),
    url(r'^feedback/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What is Markdown?",
            "description": "We love receiving feedback from our users. Whether "
                           "it be positive or negative, it helps us to grow.",
            "content_path":
                "%sfeedback.html" % (settings.HELP_DOCS_PATH),
            "category": "policies"
        },
        name="feedback"),
    url(r'^finding_topics_of_interest/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How do I find topics I'm interested in?",
            "description": "Sagebrew has a lot of content to sift through "
                           "and we know not everyone will be interested in all"
                           " the topics discussed on the site. So through the "
                           "use of tags we've attempted to improve your ability"
                           " to find topics you're interested in.",
            "content_path":
                "%sfinding_topics_of_interest.html" % (settings.HELP_DOCS_PATH),
            "category": "policies"
        },
        name="finding_topics_of_interest"),
    url(r'^how_to_search/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How do I search?",
            "description": "With all the information around on Sagebrew it's "
                           "important to know how we handle search. This article"
                           " outlines that process.",
            "content_path":
                "%show_to_search.html" % (settings.HELP_DOCS_PATH),
            "category": "policies"
        },
        name="how_to_search"),
    url(r'^markdown_formatting/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Markdown Formatting",
            "description": "Sagebrew gives users the capability to format their"
                           " content in a clean and organized way utilizing an "
                           "open standard called Markdown.",
            "content_path":
                "%smarkdown_formatting.html" % (settings.HELP_DOCS_PATH),
            "category": "policies"
        },
        name="markdown_formatting"),
    url(r'^more_help/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What if I need more help?",
            "description": "We strive to have awesome customer service and try"
                           " to be as much help to our members as possible.",
            "content_path":
                "%smore_help.html" % (settings.HELP_DOCS_PATH),
            "category": "policies"
        },
        name="more_help"),
    url(r'^reporting_suspicious_behavior/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What if I see someone doing something bad?",
            "description": "Community moderation is a big piece of what makes "
                           "Sagebrew great. Here are steps for flagging "
                           "activity you think goes against Sagebrew's "
                           "code.",
            "content_path":
                "%sreporting_suspicious_behavior.html" % (
                    settings.HELP_DOCS_PATH),
            "category": "policies"
        },
        name="reporting_suspicious_behavior"),
    url(r'^user_behavior/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What kind of behavior is expected of users?",
            "description": "We expect Sagebrew users to conduct "
                           "themselves in a mature and respectful manner, "
                           "fostering a safe and open environment.",
            "content_path":
                "%suser_behavior.html" % (settings.HELP_DOCS_PATH),
            "category": "policies"
        },
        name="user_behavior"),
    url(r'^what_is_markdown/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What is Markdown?",
            "description": "Markdown is just an easy way for us to enable "
                           "users to structure their thoughts cleanly.",
            "content_path":
                "%swhat_is_markdown.html" % (settings.HELP_DOCS_PATH),
            "category": "policies"
        },
        name="what_is_markdown"),
)