from django.conf.urls import patterns, url

from sb_comments.endpoints import (ObjectCommentsListCreate,
                                   ObjectCommentsRetrieveUpdateDestroy,
                                   comment_renderer)


urlpatterns = patterns(
    'sb_comments.endpoints',
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/comments/$',
        ObjectCommentsListCreate.as_view()),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/'
        r'comments/render/$', comment_renderer),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/comments/'
        r'(?P<comment_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectCommentsRetrieveUpdateDestroy.as_view()),
)
