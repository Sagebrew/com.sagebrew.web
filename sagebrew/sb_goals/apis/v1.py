from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_goals.endpoints import (GoalRetrieveUpdateDestroy, RoundRetrieve,
                                render_round_goals)

router = routers.SimpleRouter()

router.register(r'goals', GoalRetrieveUpdateDestroy, base_name='goal')

urlpatterns = patterns(
    'sb_goals.endpoints',
    url(r'^', include(router.urls)),
    url(r'^rounds/(?P<object_uuid>[A-Za-z0-9.@_%+-]{2,36})/$',
        RoundRetrieve.as_view(), name="round-detail"),
    url(r'^rounds/(?P<object_uuid>[A-Za-z0-9.@_%+-]{2,36})/render_goals/$',
        render_round_goals, name="round-goal-render"),
)
