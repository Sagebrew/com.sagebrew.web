from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^conversation_area/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What is the Conversation Area?",
            "description": "The Conversation Area is the place where knowledge "
                           "is shared and Solutions are provided to "
                           "leading Questions.",
            "content_path":
                "%sconversation_area.html" % (settings.HELP_DOCS_PATH),
            "category": "conversation"
        },
        name="conversation_area"),
    url(r'^starting_a_public_conversation/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How do I start a private conversation?",
            "description": "Conversations out of the public eye can be a great"
                           " way to throw ideas around with friends without "
                           "losing any reputation.",
            "content_path":
                "%sstarting_a_public_conversation." % (settings.HELP_DOCS_PATH),
            "category": "conversation"
        },
        name="starting_a_public_conversation"),
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
                "%sprotected_conversation.html" % (settings.HELP_DOCS_PATH),
            "category": "conversation"
        },
        name="protected_conversation"),

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
            "title": "What's the difference between a public and private conversation?",
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