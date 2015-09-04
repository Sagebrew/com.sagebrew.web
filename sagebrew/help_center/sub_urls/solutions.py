from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^formatting/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How do I write a good solution?",
            "description": "Writing a good solution takes time, dedication, "
                           "and a lot of thought. A good solution doesn't "
                           "appear overnight. Here are some tips on what to "
                           "keep in mind when crafting a Solution.",
            "content_path":
                "%sgood_solution.html" % settings.HELP_DOCS_PATH,
            "category": "solutions"
        },
        name="good_solution"),
    url(r'^solution_to_own_question/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Can I give a Solution to my own Question?",
            "description": "Yes you can give a Solution to your own Question.",
            "content_path":
                "%ssolution_to_own_question.html" % settings.HELP_DOCS_PATH,
            "category": "solutions"
        },
        name="solution_to_own_question"),
    url(r'^solutions_no_longer_accepted/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why are Solutions no longer being accepted from my "
                     "account?",
            "description": "There are a few reasons the Community may decide "
                           "you should be limited in providing Solutions. This "
                           "article details those reasons.",
            "content_path":
                "%ssolutions_no_longer_accepted.html" % (
                    settings.HELP_DOCS_PATH),
            "category": "solutions"
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
                "%swhen_edit_solution.html" % (
                    settings.HELP_DOCS_PATH),
            "category": "solutions"
        },
        name="when_to_edit_solutions"),
    url(r'^why_are_solutions_removed/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why and how are some solutions removed?",
            "description": "Explanation on why and how solutions are removed "
                           "from the Conversation area.",
            "content_path":
                "%swhy_solutions_removed.html" % settings.HELP_DOCS_PATH,
            "category": "solutions",
            "static_files": True,
        },
        name="why_are_solutions_removed"),
)
