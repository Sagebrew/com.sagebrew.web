from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^closed_question/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What does it mean if a Question is Closed?",
            "description": "Closed questions are questions that don't warrant "
                           "deletion but might be lacking in quality.",
            "content_path":
                "%s/static/rendered_docs/why_closed_question.html" % (
                    settings.STATIC_URL)
        },
        name="closed_question"),
    url(r'^closure_of_a_question/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What if I disagree with the closure of a question? "
                     "How can I reopen it?",
            "description": "Closed questions cannot be reopened. If your "
                           "Question has been flagged for closure you must "
                           "provide evidence that it should not be closed "
                           "prior to the Admin Council concluding their vote "
                           "on the content.",
            "content_path":
                "%s/static/rendered_docs/closure_of_a_question.html" % (
                    settings.STATIC_URL)
        },
        name="closure_of_a_question"),
    url(r'^context_to_a_question/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why is adding Context to Questions important?",
            "description": "Bringing context to a question allows others to"
                           "gain a better understanding of the scope of the"
                           "question and provide a more accurate solution",
            "content_path":
                "%s/static/rendered_docs/context_to_a_question.html" % (
                    settings.STATIC_URL)
        },
        name="context_to_a_question"),
    url(r'^duplicate_questions/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why are some questions marked as duplicate?",
            "description": "It helps to keep  conversations on track if "
                           "duplicate questions are marked and users are"
                           " informed where the core conversation is"
                           " happening.",
            "content_path":
                "%s/static/rendered_docs/duplicate_question.html" % (
                    settings.STATIC_URL)
        },
        name="duplicate_questions"),
    url(r'^good_question/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How do I create a good question?",
            "description": "A frequently asked question regarding what is"
                           "expected from community members when they are"
                           "asking a question.",
            "content_path":
                "%s/static/rendered_docs/good_question.html" % (
                    settings.STATIC_URL)},
        name="good_question"),
    url(r'^no_traffic/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What should I do if my Question gets no traffic?",
            "description": "Sometimes our Questions don't receive a lot of "
                           "traffic. This can be caused by a multitude of "
                           "reasons but some common ones are described here.",
            "content_path":
                "%s/static/rendered_docs/no_traffic.html" % (
                    settings.STATIC_URL)
        },
        name="no_traffic"),
    url(r'^protected_conversation/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": 'What does it mean if a Conversation is "Protected"?',
            "description": "Admin Council members have the ability to Protect "
                           "Conversations that have not yet reached Seasoned "
                           "status but need a bit more credibility to "
                           "participate in. This can happen "
                           "on valid Questions that attract a lot of attention "
                           "but bolster too much noise.",
            "content_path":
                "%s/static/rendered_docs/protected_conversation.html" % (
                    settings.STATIC_URL)
        },
        name="protected_conversation"),
    url(r'^quality_standards/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why do I see a message that says my question does not "
                     "meet quality standards?",
            "description": "Sagebrew attempts to maintain a level of quality "
                           "within the conversations on the site. This is "
                           "achieved through active contribution from the "
                           "community and notifications to users about "
                           "breaking the quality standards.",
            "content_path":
                "%s/static/rendered_docs/quality_standards_message.html" % (
                    settings.STATIC_URL)
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
                "%s/static/rendered_docs/questions_avoid_asking.html" % (
                    settings.STATIC_URL)
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
                "%s/static/rendered_docs/questions_no_longer_accepted.html" % (
                    settings.STATIC_URL)
        },
        name="questions_no_longer_accepted"),
    url(r'^seasoned_conversation/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": 'What does it mean if a Conversation is "Seasoned"?',
            "description": "Conversations eventually obtain a solid foundation "
                           "where many users have agreed on a Solution. If "
                           "this occurs a Conversation becomes Seasoned.",
            "content_path":
                "%s/static/rendered_docs/seasoned_description.html" % (
                    settings.STATIC_URL)
        },
        name="seasoned_conversation"),
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
                "%s/static/rendered_docs/solution_to_question.html" % (
                    settings.STATIC_URL)
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
                "%s/static/rendered_docs/tags_and_how_to_use_them.html" % (
                    settings.STATIC_URL)
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
                "%s/static/rendered_docs/topics_to_ask_about.html" % (
                    settings.STATIC_URL)
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
                "%s/static/rendered_docs/traffic_no_solutions.html" % (
                    settings.STATIC_URL)
        },
        name="traffic_no_solutions"),
    url(r'^why_are_questions_deleted/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why and how are some Questions deleted?",
            "description": "There are few reasons why a Question may be "
                           "deleted. This article details what those reasons"
                           " are.",
            "content_path":
                "%s/static/rendered_docs/why_are_questions_deleted.html" % (
                    settings.STATIC_URL)
        },
        name="why_are_questions_deleted"),
)