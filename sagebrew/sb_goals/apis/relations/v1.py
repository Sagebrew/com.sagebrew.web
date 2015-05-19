from django.conf.urls import patterns, url

from sb_goals.endpoints import GoalListMixin, RoundListCreate


urlpatterns = patterns(
    'sb_goals.endpoints',
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/goals/$',
        GoalListMixin.as_view(), name="goals-list"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/rounds/$',
        RoundListCreate.as_view(), name="rounds-list")
)