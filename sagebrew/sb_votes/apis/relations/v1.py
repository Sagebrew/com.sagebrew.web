from django.conf.urls import url

from sagebrew.sb_votes.endpoints import (ObjectVotesListCreate)


urlpatterns = [
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/votes/$',
        ObjectVotesListCreate.as_view()),
]
