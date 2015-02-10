from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^why_are_solutions_removed/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why and how are some solutions removed?",
            "description": "Explanation on why and how solutions are removed "
                           "from the Conversation area.",
            "content_path":
                "%s/static/rendered_docs/how_solutions_removed.html" % (
                    settings.STATIC_URL)
        },
        name="why_are_solutions_removed"),
    url(r'^solutions_no_longer_accepted/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why are Solutions no longer being accepted from my "
                     "account?",
            "description": "There are a few reasons the Community may decide "
                           "you should be limited in providing Solutions. This "
                           "article details those reasons.",
            "content_path":
                "%s/static/rendered_docs/solutions_no_longer_accepted.html" % (
                    settings.STATIC_URL)
        },
        name="solutions_no_longer_accepted"),
    url(r'^when_to_edit_solutions/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "When should I edit my Solution?",
            "description": "Solutions are always evolving, taking in feedback "
                           "and growing with a Conversation. Here are some tips"
                           " on when you should be editing your Solution",
            "content_path":
                "%s/static/rendered_docs/when_edit_solutions.html" % (
                    settings.STATIC_URL)
        },
        name="when_to_edit_solutions"),
)