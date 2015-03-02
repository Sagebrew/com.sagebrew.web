from django.conf.urls import patterns, url

from .views import (action_page)

urlpatterns = patterns(
    'sb_questions.views',
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{1,30})/$', action_page,
        name='action_page'),
)