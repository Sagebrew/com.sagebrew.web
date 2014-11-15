from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns(
    url(r'^good_question/', TemplateView.as_view(
        template_name="good_question.html")),
)