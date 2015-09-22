from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView, RedirectView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^advertising/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Can I Advertise on Sagebrew?",
            "description": "We attempt to stay as neutral as possible. "
                           "We don't allow third "
                           "party advertising so that we ensure our focus stays"
                           " on our users and not those trying to exploit "
                           "them.",
            "content_path":
                "%sadvertising.html" % settings.HELP_DOCS_PATH,
            "category": "policies"
        },
        name="advertising"),
    url(r'^be-nice/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Be Nice",
            "description": "We try to foster a collaborative environment but "
                           "to do that we need the community to give us a "
                           "helping hand.",
            "content_path":
                "%sbe_nice.html" % settings.HELP_DOCS_PATH,
            "category": "policies"
        },
        name="be_nice"),
    url(r'^do-not-spam/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How to not be a Spammer",
            "description": "Some notes on what we consider a spammer and how "
                           "you can avoid being branded as one.",
            "content_path":
                "%sdont_spam.html" % settings.HELP_DOCS_PATH,
            "category": "policies"
        },
        name="do_not_spam"),
    url(r'^feedback/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Providing Feedback",
            "description": "We love receiving feedback from our users. Whether "
                           "it be positive or negative, it helps us to grow.",
            "content_path":
                "%sfeedback.html" % settings.HELP_DOCS_PATH,
            "category": "policies"
        },
        name="feedback"),
    url(r'^finding-topics-of-interest/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How do I find topics I'm interested in?",
            "description": "Sagebrew has a lot of content to sift through "
                           "and we know not everyone will be interested in all"
                           " the topics discussed on the site. So through the "
                           "use of tags we've attempted to improve your ability"
                           " to find topics you're interested in.",
            "content_path":
                "%sfinding_topics_of_interest.html" % settings.HELP_DOCS_PATH,
            "category": "policies"
        },
        name="finding_topics_of_interest"),
    url(r'^how-to-search/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How do I search?",
            "description": "With all the information around on Sagebrew it's "
                           "important to know how we handle search. This "
                           "article outlines that process.",
            "content_path":
                "%show_to_search.html" % settings.HELP_DOCS_PATH,
            "category": "policies"
        },
        name="how_to_search"),
    url(r'^markdown-formatting/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Markdown Formatting",
            "description": "Sagebrew gives users the capability to format their"
                           " content in a clean and organized way utilizing an "
                           "open standard called Markdown.",
            "content_path":
                "%smarkdown_formatting.html" % settings.HELP_DOCS_PATH,
            "category": "policies"
        },
        name="markdown_formatting"),
    url(r'^support/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What if I need more help?",
            "description": "We strive to have awesome customer service and try"
                           " to be as much help to our members as possible.",
            "content_path":
                "%smore_help.html" % settings.HELP_DOCS_PATH,
            "category": "policies"
        },
        name="support"),
    url(r'^reporting-suspicious-behavior/$', TemplateView.as_view(
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
    url(r'^user-behavior/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What kind of behavior is expected of users?",
            "description": "We expect Sagebrew users to conduct "
                           "themselves in a mature and respectful manner, "
                           "fostering a safe and open environment.",
            "content_path":
                "%suser_behavior.html" % settings.HELP_DOCS_PATH,
            "category": "policies"
        },
        name="user_behavior"),
    url(r'^what-is-markdown/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What is Markdown?",
            "description": "Markdown is just an easy way for us to enable "
                           "users to structure their thoughts cleanly.",
            "content_path":
                "%swhat_is_markdown.html" % settings.HELP_DOCS_PATH,
            "category": "policies"
        },
        name="what_is_markdown"),
    url(r'^be_nice/$', RedirectView.as_view(
        url='/help/policies/be-nice/', permanent=True),
        name='be_nice_redirect'),
    url(r'^do_not_spam/$', RedirectView.as_view(
        url='/help/policies/do-not-spam/', permanent=True),
        name='do_not_spam_redirect'),
    url(r'^finding_topics_of_interest/$', RedirectView.as_view(
        url='/help/policies/finding-topics-of-interest/', permanent=True),
        name='finding_topics_of_interest_redirect'),
    url(r'^how_to_search/$', RedirectView.as_view(
        url='/help/policies/how-to-search/', permanent=True),
        name='how_to_search_redirect'),
    url(r'^markdown_formatting/$', RedirectView.as_view(
        url='/help/policies/markdown-formatting/', permanent=True),
        name='markdown_formatting_redirect'),
    url(r'^reporting_suspicious_behavior/$', RedirectView.as_view(
        url='/help/policies/reporting-suspicious-behavior/', permanent=True),
        name='reporting_suspicious_behavior_redirect'),
    url(r'^user_behavior/$', RedirectView.as_view(
        url='/help/policies/user-behavior/', permanent=True),
        name='user_behavior_redirect'),
    url(r'^what_is_markdown/$', RedirectView.as_view(
        url='/help/policies/what-is-markdown/', permanent=True),
        name='what_is_markdown_redirect'),
)
