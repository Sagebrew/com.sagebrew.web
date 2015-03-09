from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^why_join/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why should I create an account?",
            "description": "There are many reasons why you should sign up and"
                           " create a Sagebrew account. We've laid out some of"
                           " the most important reasons in this article.",
            "content_path":
                "%screate_an_account.html" % (settings.HELP_DOCS_PATH),
            "category": "account"
        },
        name="create_an_account"),
    url(r'^restriction_on_asking/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Why is the system asking me to wait a day or more before "
                     "asking another question?",
            "description": "There are couple reasons why you may not be able "
                           "to contribute anymore today. These reasons are laid"
                           " out in this article.",
            "content_path":
                "%srestriction_on_asking.html" % (settings.HELP_DOCS_PATH),
            "category": "account"
        },
        name="restriction_on_asking"),

)

if settings.DEBUG is True:
    urlpatterns += patterns(
        url(r'^change_password/$', TemplateView.as_view(
            template_name="help_page.html"),
            kwargs={
                "title": "How do I change my password?",
                "description": "Within you settings there is an area to change "
                               "your password. This article will guide you "
                               "through the process.",
                "content_path":
                    "%schange_password.html" % (settings.HELP_DOCS_PATH),
                "category": "account"
            },
            name="change_password"),
        url(r'^delete_account/$', TemplateView.as_view(
            template_name="help_page.html"),
            kwargs={
                "title": "How do I delete my account?",
                "description": "We're really sad to see you go but try to make it "
                               "as easy as possible for you to delete your account"
                               " if you want to. This article will walk you "
                               "through the steps.",
                "content_path":
                    "%sdelete_account.html" % (settings.HELP_DOCS_PATH),
                "category": "account"
            },
            name="delete_account"),
        url(r'^reset_password/$', TemplateView.as_view(
            template_name="help_page.html"),
            kwargs={
                "title": "How do I reset my password?",
                "description": "Occasionally we all forget what our password was. "
                               "This article will help walk you through resetting "
                               "yours.",
                "content_path":
                    "%sreset_password.html" % (settings.HELP_DOCS_PATH),
                "category": "account"
            },
            name="reset_password"),
    )

