from django.conf.urls import url, include

from rest_framework import routers

from sagebrew.sb_posts.endpoints import (PostsViewSet)


router = routers.SimpleRouter()
router.register(r'posts', PostsViewSet, base_name="post")


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^posts/', include('sagebrew.sb_comments.apis.relations.v1')),
    url(r'^posts/', include('sagebrew.sb_flags.apis.relations.v1')),
    url(r'^posts/', include('sagebrew.sb_votes.apis.relations.v1')),
]
