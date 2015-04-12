from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_comments.endpoints import (ObjectCommentsRetrieveUpdateDestroy,
                                   ObjectCommentsListCreate, comment_renderer)
from sb_posts.endpoints import (PostsViewSet)

router = routers.SimpleRouter()

router.register(r'posts', PostsViewSet, base_name="post")

urlpatterns = patterns(
    'sb_posts.endpoints',
    url(r'^', include(router.urls)),
    url(r'^posts/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/comments/$',
        ObjectCommentsListCreate.as_view(), name="post-comments"),
    url(r'^posts/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/'
        r'comments/render/$',
        comment_renderer, name="post-comments-html"),
    url(r'^posts/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/comments/'
        r'(?P<comment_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectCommentsRetrieveUpdateDestroy.as_view(),
        name="post-comment"),
)