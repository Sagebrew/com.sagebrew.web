from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_posts.endpoints import (PostsViewSet)


router = routers.SimpleRouter()
router.register(r'posts', PostsViewSet, base_name="post")


urlpatterns = patterns(
    'sb_posts.endpoints',
    url(r'^', include(router.urls)),
    (r'^posts/', include('sb_comments.apis.relations.v1')),
    (r'^posts/', include('sb_flags.apis.relations.v1')),
    (r'^posts/', include('sb_votes.apis.relations.v1')),
)
