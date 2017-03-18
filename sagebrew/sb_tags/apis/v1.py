from django.conf.urls import url, include

from rest_framework import routers

from sagebrew.sb_tags.endpoints import TagViewSet

router = routers.SimpleRouter()

router.register(r'tags', TagViewSet, base_name="tag")


urlpatterns = [
    url(r'^', include(router.urls)),
]
