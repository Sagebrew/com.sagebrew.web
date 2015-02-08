from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from django.conf import settings

'''
content_path is used in sync with the ssi tag in help_page.html to include
the rendered html files from S3. Using python's
http://pythonhosted.org//Markdown/cli.html we can convert the md files into
html in the static folder and then run these right out of the template. This
allows for us to still have a side bar, nav bar, and footer with user centric
material displayed while manging our docs in a markdown format making it easy
for our content creators to manage the information.

'''
urlpatterns = patterns(
    'help_center.views',
    url(r'^duplicate_questions/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why are some questions marked as duplicate?",
            "description": "It helps to keep  conversations on track if "
                           "duplicate questions are marked and users are"
                           " informed where the core conversation is happening.",
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
            "content_path": ""},
        name="good_question"),
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
    url(r'^why_are_solutions_removed/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why and how are some solutions removed?",
            "description": "Explanation on why and how solutions are removed "
                           "from the Conversation area.",
            "content_path":
                "%s/static/rendered_docs/how_solutions_removed.html" % (
                    settings.STATIC_URL)
        },
        name="why_are_solutions_removed"),
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
    url(r'^solutions_no_longer_accepted/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why are Solutions no longer being accepted from my "
                     "account?",
            "description": "There are a few reasons the Community may decide "
                           "you should be limited in providing Solutions. This "
                           "article details those reasons.",
            "content_path":
                "%s/static/rendered_docs/solutions_no_longer_accepted.html" % (
                    settings.STATIC_URL)
        },
        name="solutions_no_longer_accepted"),
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
    url(r'^when_to_edit_solutions/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "When should I edit my Solution?",
            "description": "Solutions are always evolving, taking in feedback "
                           "and growing with a Conversation. Here are some tips"
                           " on when you should be editing your Solution",
            "content_path":
                "%s/static/rendered_docs/when_edit_solutions.html" % (
                    settings.STATIC_URL)
        },
        name="when_to_edit_solutions"),
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
    (r'^help/', include('help_center.sub_urls.asking')),
)

"""
TODO: We need to ensure we do the following to allow indexing and easier search
Title: My super title
Date: 2010-12-03 10:20
Modified: 2010-12-05 19:30
Category: Python
Tags: pelican, publishing
Slug: my-super-post
Authors: Alexis Metaireau, Conan Doyle
Summary: Short version for index and feeds

See http://docs.getpelican.com/en/3.5.0/content.html#file-metadata for html
metadata result
"""