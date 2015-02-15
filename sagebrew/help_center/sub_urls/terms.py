from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^trust_and_safety/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Trust and Safety",
            "description": "Sagebrew works very hard to promote "
                           "and maintain a safe and secure "
                           "environment for its users. Sometimes "
                           "we need the help of the community to "
                           "facilitate this environment.",
            "content_path":
                "%s/static/rendered_docs/trust_and_safety.html" % (
                    settings.STATIC_URL)
        },
        name="trust_and_safety"),

)