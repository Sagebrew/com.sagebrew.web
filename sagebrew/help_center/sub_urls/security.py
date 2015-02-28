from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^vulnerabilities/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How do I report a possible security vulnerability?",
            "description": "Security is essential and we do our best to "
                           "protect our users. But there could be things we "
                           "miss and we hope the community will help us "
                           "if they find any holes.",
            "content_path":
                "%ssecurity_vulnerability.html" % (settings.HELP_DOCS_PATH),
            "category": "security"
        },
        name="security_vulnerability"),
)