from django.conf.urls import patterns, url

from .views import (manage_goals)

urlpatterns = patterns(
    'sb_goals.views',
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage_goals/',
        manage_goals, name="manage_goals")
)
