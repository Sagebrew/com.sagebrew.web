from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_oauth.endpoints import ApplicationViewSet

router = routers.SimpleRouter()

router.register(r'applications', ApplicationViewSet, base_name="application")

urlpatterns = patterns(
    'sb_oauth.views',
    url(r'^', include(router.urls)),
)