from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^participate_in_the_conversation/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Participate in the Conversation",
            "description": "Everyone starts out with the privilege of partaking"
                           " in the conversation on Sagebrew.",
            "content_path":
                "%s/static/rendered_docs/"
                "participate_in_the_conversation.html" % (
                    settings.STATIC_URL)
        },
        name="participate_in_the_conversation"),
)