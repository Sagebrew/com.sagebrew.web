from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_tag.endpoints import TagViewSet

router = routers.SimpleRouter()

router.register(r'tags', TagViewSet, base_name="tag")

urlpatterns = patterns(
    'sb_tag.endpoints',
    url(r'^', include(router.urls)),
)