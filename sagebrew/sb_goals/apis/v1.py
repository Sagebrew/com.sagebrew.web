from django.conf.urls import patterns, url

from sb_goals.endpoints import (GoalRetrieveUpdateDestroy,
                                RoundRetrieveUpdateDestroy)


urlpatterns = patterns(
    'sb_goals.endpoints',
    url(r'^goals/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        GoalRetrieveUpdateDestroy.as_view(), name="goal-detail"),
    url(r'^rounds/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        RoundRetrieveUpdateDestroy.as_view(), name="round-detail")
)
