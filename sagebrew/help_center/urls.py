from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns(
    url(r'^good_question/', TemplateView.as_view(
        template_name="good_question.html"),
        kwargs={"title": "How do I create a good question?",
                "description": "A frequently asked question regarding what is"
                               "expected from community members when they are"
                               "asking a question."}, name="good_question"),
)