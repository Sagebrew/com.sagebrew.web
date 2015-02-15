from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^be_nice/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Markdown Formatting",
            "description": "We try to foster a collaborative environment but "
                           "to do that we need the community to give us a "
                           "helping hand.",
            "content_path":
                "%s/static/rendered_docs/be_nice.html" % (
                    settings.STATIC_URL)
        },
        name="be_nice"),
    url(r'^advertising/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Can I Advertise on Sagebrew",
            "description": "We attempt to stay as neutral as possible and "
                           "believe allowing advertisement on the site would "
                           " hinder our credibility. We don't allow third "
                           "party advertising so that we ensure our focus stays"
                           " on our users and not those trying to exploit "
                           "them.",
            "content_path":
                "%s/static/rendered_docs/advertising.html" % (
                    settings.STATIC_URL)
        },
        name="advertising"),
    url(r'^markdown_formatting/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Markdown Formatting",
            "description": "Sagebrew gives users the capability to format their"
                           " content in a clean and organized way utilizing an "
                           "open standard called Markdown.",
            "content_path":
                "%s/static/rendered_docs/markdown_formatting.html" % (
                    settings.STATIC_URL)
        },
        name="markdown_formatting"),

)