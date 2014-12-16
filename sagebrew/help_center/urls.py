from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns(
    'help_center.views',
    url(r'^good_question/$', TemplateView.as_view(
        template_name="asking/good_question.html"),
        kwargs={"title": "How do I create a good question?",
                "description": "A frequently asked question regarding what is"
                               "expected from community members when they are"
                               "asking a question."}, name="good_question"),
    url(r'^starting_a_private_conversation/$', TemplateView.as_view(
        template_name="conversations/starting_a_private_conversation.html"),
        kwargs={"title": "How do I create a good question?",
                "description": "Explanation on how to start a private"
                               " conversation between friends."},
        name="starting_private_conversation"),
)