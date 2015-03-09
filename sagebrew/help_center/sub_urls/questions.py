from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^context/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why is adding Context to Questions important?",
            "description": "Bringing context to a question allows others to"
                           "gain a better understanding of the scope of the"
                           "Question and provide more accurate Solutions",
            "content_path":
                "%scontext_to_a_question.html" % (settings.HELP_DOCS_PATH),
            "category": "questions"
        },
        name="context_to_a_question"),
    url(r'^duplicates/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why are some things marked as duplicate?",
            "description": "It helps to keep  conversations on track. "
                           "Duplicate questions are marked and users are"
                           " informed where the core conversation is"
                           " happening.",
            "content_path":
                "%sduplicates.html" % (settings.HELP_DOCS_PATH),
            "category": "questions"
        },
        name="duplicates"),
    url(r'^good_question/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How do I create a good question?",
            "description": "A frequently asked question regarding what is"
                           "expected from community members when they are"
                           "asking a question.",
            "content_path":
                "%sgood_question.html" % (settings.HELP_DOCS_PATH),
            "category": "questions"
        },
        name="good_question"),
    url(r'^no_traffic/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What should I do if my Question gets no traffic?",
            "description": "Sometimes our Questions don't receive a lot of "
                           "traffic. This can be caused by a multitude of "
                           "reasons but some common ones are described here.",
            "content_path":
                "%sno_traffic.html" % (settings.HELP_DOCS_PATH),
            "category": "questions"
        },
        name="no_traffic"),
    url(r'^quality_standards/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why do I see a message that says my question does not "
                     "meet quality standards?",
            "description": "Sagebrew attempts to maintain a level of quality "
                           "within the conversations on the site. This is "
                           "achieved through active contribution from the "
                           "Community and notifications to users about "
                           "breaking the quality standards.",
            "content_path":
                "%squality_standards_message.html" % (settings.HELP_DOCS_PATH),
            "category": "questions"
        },
        name="quality_standards"),
    url(r'^questions_avoid_asking/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What types of Questions should I avoid asking?",
            "description": "There are certain questions that can be easily "
                           "answered through a Google search; these are not "
                           "meant for Sagebrew.",
            "content_path":
                "%squestions_avoid_asking.html" % (settings.HELP_DOCS_PATH),
            "category": "questions"
        },
        name="questions_avoid_asking"),
    url(r'^questions_no_longer_accepted/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why are Questions no longer being accepted by my "
                     "account?",
            "description": "There are a few reasons why Sagebrew may limit "
                           "a user from sparking a conversation. This "
                           "article details those reasons.",
            "content_path":
                "%squestions_no_longer_accepted.html" % (
                    settings.HELP_DOCS_PATH),
            "category": "questions"
        },
        name="questions_no_longer_accepted"),
    url(r'^solution_to_question/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What should I do when someone provides a solution to my"
                     " question?",
            "description": "Solutions provide a chance for collaboration and "
                           "are an exciting opportunity. Here are some pointers"
                           " for what to do when someone provides one to your"
                           " Question.",
            "content_path":
                "%ssolution_to_question.html" % (settings.HELP_DOCS_PATH),
            "category": "questions"
        },
        name="solution_to_question"),
    url(r'^tags/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What are Tags, and how should I use them?",
            "description": "Tags help Sagebrew help the community in many ways,"
                           "including improved search results and better "
                           "suggestions.",
            "content_path":
                "%stags_and_how_to_use_them.html" % (settings.HELP_DOCS_PATH),
            "category": "questions"
        },
        name="tags_and_how_to_use_them"),
    url(r'^topics_to_ask_about/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What topics can I ask about here?",
            "description": "Sagebrew is a place for engaging conversations, "
                           "here are some of the topics the Community likes "
                           "to discuss.",
            "content_path":
                "%stopics_to_ask_about.html" % (settings.HELP_DOCS_PATH),
            "category": "questions"
        },
        name="topics_to_ask_about"),
    url(r'^traffic_no_solutions/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What should I do if no one provides a Solution to my "
                     "Question?",
            "description": "Sometimes important Questions with a large amount "
                           "of interested users are really difficult. If you're"
                           " seeing traffic on your Question but no Solutions "
                           "being proposed, try some of these ideas.",
            "content_path":
                "%straffic_no_solutions.html" % (settings.HELP_DOCS_PATH),
            "category": "questions"
        },
        name="traffic_no_solutions"),
)


if settings.DEBUG is True:
    url(r'^closure_of_a_question/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What if I disagree with the closure of a question? "
                     "How can I reopen it?",
            "description": "If something you've contributed has been closed, "
                           "the only way to get it reopened is by explaining "
                           "your case to the Admin Council. They have the right"
                           " to disagree with your case and keep the content "
                           "closed.",
            "content_path":
                "%sclosure_of_a_question.html" % (settings.HELP_DOCS_PATH),
            "category": "questions"
        },
        name="closure_of_a_question"),