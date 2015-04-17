from django.conf.urls import patterns, url

from sb_votes.endpoints import (ObjectVotesListCreate)


urlpatterns = patterns(
    'sb_votes.endpoints',
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/votes/$',
        ObjectVotesListCreate.as_view())
)