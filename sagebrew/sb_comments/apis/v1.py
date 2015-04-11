from django.conf.urls import patterns, url

from rest_framework import routers


from sb_posts.endpoints import (PostsViewSet)

from sb_comments.endpoints import (ObjectCommentsRetrieveUpdateDestroy)

router = routers.SimpleRouter()

router.register(r'posts', PostsViewSet, base_name="post")

"""
See sb_questions/apis/v1.py for reasoning on excluding
ObjectCommentsRetrieveUpdateDestroy
"""

urlpatterns = patterns(
    'sb_comments.endpoints',
    url(r'^comments/(?P<comment_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectCommentsRetrieveUpdateDestroy.as_view(), name="comment-detail"),
)