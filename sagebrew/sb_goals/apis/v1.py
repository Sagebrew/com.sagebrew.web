from django.conf.urls import patterns, url

from sb_goals.endpoints import (GoalRetrieveUpdateDestroy, RoundRetrieve,
                                render_round_goals)


urlpatterns = patterns(
    'sb_goals.endpoints',
    url(r'^goals/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        GoalRetrieveUpdateDestroy.as_view(), name="goal-detail"),
    url(r'^rounds/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        RoundRetrieve.as_view(), name="round-detail"),
    url(r'^rounds/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/render_goals/$',
        render_round_goals, name="round-goal-render"),
)
