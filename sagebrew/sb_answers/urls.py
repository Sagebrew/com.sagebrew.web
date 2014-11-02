from django.conf.urls import patterns, url

from .views import (save_answer_view, edit_answer_view)

urlpatterns = patterns(
    'sb_answers.views',
    url(r'^submit_answer_api/$', save_answer_view, name="save_answer"),
    url(r'^edit_answer_api/$', edit_answer_view, name="edit_answer"),
)