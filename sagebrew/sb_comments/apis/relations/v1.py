from django.conf.urls import url

from sagebrew.sb_comments.endpoints import (
    ObjectCommentsListCreate, ObjectCommentsRetrieveUpdateDestroy)


urlpatterns = [
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/comments/$',
        ObjectCommentsListCreate.as_view()),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/comments/'
        r'(?P<comment_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectCommentsRetrieveUpdateDestroy.as_view()),
]
