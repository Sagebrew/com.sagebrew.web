from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
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
)