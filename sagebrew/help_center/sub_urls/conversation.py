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
                "%s/static/rendered_docs/conversation_area.html" % (
                    settings.STATIC_URL)
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
                "%s/static/rendered_docs/starting_a_public_conversation."
                "html" % (settings.STATIC_URL)
        },
        name="starting_a_public_conversation"),

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
                "%s/static/rendered_docs/private_to_public.html" % (
                    settings.STATIC_URL)
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
                "%s/static/rendered_docs/starting_a_private_conversation."
                "html" % (settings.STATIC_URL)
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
                "%s/static/rendered_docs/public_vs_private.html" % (
                    settings.STATIC_URL)
        },
        name="public_vs_private"),
    '''