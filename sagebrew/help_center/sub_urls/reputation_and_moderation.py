from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^reputation_changed_user_removed/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": 'Why do I have a reputation change on my reputation page '
                     'that says "User was removed"?',
            "description": "It's unfortunate but some users abuse the system. "
                           "This sometimes affects innocent bystander's, we're"
                           "sorry you were one of them.",
            "content_path":
                "%s/static/rendered_docs/reputation_change_user_remove.html" % (
                    settings.STATIC_URL)
        },
        name="reputation_changed_user_removed"),
)