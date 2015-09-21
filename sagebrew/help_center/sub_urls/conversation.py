from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView, RedirectView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^closed/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What does it mean if something is Closed?",
            "description": "Something that is closed can no longer be "
                           "interacted with.",
            "content_path":
                "%sclosed.html" % settings.HELP_DOCS_PATH,
            "category": "conversation"
        },
        name="closed"),
    url(r'^conversation-cloud/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What is the Conversation Cloud?",
            "description": "The Conversation Cloud is the place where "
                           "knowledge "
                           "is shared and Solutions are provided to "
                           "leading Questions.",
            "content_path":
                "%sconversation_area.html" % settings.HELP_DOCS_PATH,
            "category": "conversation"
        },
        name="conversation_area"),
    url(r'^deletions/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why and how are some contributes deleted?",
            "description": "There are few reasons why a contribution may be "
                           "deleted. This article details what those reasons"
                           " are.",
            "content_path":
                "%sdeletions.html" % settings.HELP_DOCS_PATH,
            "category": "conversation"
        },
        name="deletions"),
    url(r'^one-question-per-week/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why have I been limited to one question per week?",
            "description": "If you've noticed you've been limited to one "
                           "question per week, this article will help you "
                           "understand why.",
            "content_path":
                "%sone_question_per_week.html" % settings.HELP_DOCS_PATH,
            "category": "conversation"
        },
        name="one_question_per_week"),
    url(r'^research/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Research Study Methods and Value",
            "description": "There are many forms of research that can assist in"
                           " providing context to your Question or backing your"
                           " Solution.",
            "content_path":
                "%sresearch.html" % settings.HELP_DOCS_PATH,
            "category": "conversation"
        },
        name="research"),
    url(r'^starting-a-public-conversation/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How do I start a public conversation?",
            "description": "It's easy to start a Public Conversation by "
                           "following these instructions. But please make sure "
                           "to look around first and make sure there isn't "
                           "already one brewing.",
            "content_path":
                "%sstarting_a_public_conversation.html" % (
                    settings.HELP_DOCS_PATH),
            "category": "conversation",
            "static_files": True
        },
        name="starting_a_public_conversation"),
    url(r'^protected/$', TemplateView.as_view(
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
                "%sprotected.html" % settings.HELP_DOCS_PATH,
            "category": "conversation"
        },
        name="protected"),
    url(r'^seasoned/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": 'What does it mean if a Conversation is "Seasoned"?',
            "description": "Conversations eventually obtain a solid foundation "
                           "where many users have agreed on a Solution. If "
                           "this occurs a Conversation becomes Seasoned.",
            "content_path":
                "%sseasoned.html" % settings.HELP_DOCS_PATH,
            "category": "questions"
        },
        name="seasoned"),
    url(r'^spam/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why has my contribution been removed due to 'spam'?",
            "description": "The Community has indicated your "
                           "contribution looks like spam and the "
                           "Admin Council has agreed with them.",
            "content_path":
                "%scontribution_spam_block.html" % settings.HELP_DOCS_PATH,
            "category": "conversation"
        },
        name="spam"),
    url(r'^conversation_area/$', RedirectView.as_view(
        url='/help/conversation/conversation-cloud/', permanent=True),
        name='conversation_area_redirect'),
    url(r'^one_question_per_week/$', RedirectView.as_view(
        url='/help/conversation/one-question-per-week/', permanent=True),
        name='one_question_per_week_redirect'),
    url(r'^starting_a_public_conversation/$', RedirectView.as_view(
        url='/help/conversation/starting-a-public-conversation/', permanent=True),
        name='starting_a_public_conversation_redirect'),
)

'''
    TODO on hold until private conversation is live.
    url(r'^private_to_public/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Can I convert a private conversation into a public one?",
            "description": "To protect user's privacy we do not allow private "
                           "conversations to be converted to public ones.",
            "content_path":
                "%sprivate_to_public.html" % (settings.HELP_DOCS_PATH)
        },
        name="private_to_public"),
    url(r'^starting_a_private_conversation/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How do I start a private conversation?",
            "description": "Conversations out of the public eye can be a great"
                           " way to throw ideas around with friends without "
                           "losing any reputation.",
            "content_path":
                "%sstarting_a_private_conversation." % (settings.HELP_DOCS_PATH)
        },
        name="starting_a_private_conversation"),
    url(r'^public_vs_private/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What's the difference between a public and private
            conversation?",
            "description": "Sagebrew offers both private and public "
                           "Conversations. There are two key differences. One "
                           "is that Public Conversations can be viewed by "
                           "everyone and Private Conversations can only be seen"
                           " by friends on your Friends List. The other is "
                           "that Private Conversations don't affect your "
                           "Reputation while Public Conversations do. ",
            "content_path":
                "%spublic_vs_private.html" % (settings.HELP_DOCS_PATH)
        },
        name="public_vs_private"),
    '''
