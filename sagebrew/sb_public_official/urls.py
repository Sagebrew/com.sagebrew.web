from django.conf.urls import patterns, url

from .views import (saga, about, updates)

urlpatterns = patterns(
    'sb_questions.views',
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{1,36})/$', saga,
        name='action_saga'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{1,36})/about/$', about,
        name='action_about'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{1,36})/updates/', updates,
        name='action_updates'),
)