from django.conf.urls import url, include

from rest_framework import routers

from sagebrew.sb_oauth.endpoints import ApplicationViewSet

router = routers.SimpleRouter()

router.register(r'applications', ApplicationViewSet, base_name="application")

urlpatterns = [
    url(r'^', include(router.urls)),
]
