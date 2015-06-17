from django.conf.urls import patterns, url

from sb_goals.endpoints import GoalListCreateMixin, RoundListCreate


urlpatterns = patterns(
    'sb_goals.endpoints',
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{1,36})/goals/$',
        GoalListCreateMixin.as_view(), name="goal-list"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{1,36})/rounds/$',
        RoundListCreate.as_view(), name="round-list")
)
